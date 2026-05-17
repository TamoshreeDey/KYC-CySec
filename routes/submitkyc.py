from flask import Flask, request, jsonify, Blueprint
from datetime import datetime, timezone
from services.validator import KYCValidator
from services.crypto import CryptoService
from services.database import DatabaseManager

crypto=CryptoService()
kycval=KYCValidator()
db=DatabaseManager()

kyc_app= Blueprint('kyc',__name__)

@kyc_app.route('/submit-kyc', methods=['POST'])
def save_kyc_route():
    data=request.get_json(silent=True)
    
    #check if the form is empty
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # 2. Field Presence Validation (Are required keys there?)
    required_fields = ['first_name', 'last_name', 'dob', 'aadhar']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Missing critical field: {field}"}), 400

    # 3. Data Type / Format Validation
    try:
        birth_date = datetime.strptime(data.get('dob'), "%Y-%m-%d")
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid Date of Birth format. Use YYYY-MM-DD"}), 400
    
    #4. Check for adhar and pan validity
    if not kycval.validate_aadhar(data.get('aadhar')):
        return jsonify({"error":"Invalid Adhar format"}), 400
    if not kycval.validate_pan(data.get("pan")):
        return jsonify({"error":"Invalid Pan Format"}), 400
    
    full_name= {"first_name":data.get('first_name'), 
                "last_name":data.get('last_name')}
    father_name= {"first_name":data.get('f_first_name'), 
                "last_name":data.get('f_last_name')}
    mother_name= {"first_name":data.get('m_first_name'), 
                "last_name":data.get('m_last_name')}
    guardian_name={"first_name":data.get('g_first_name'), 
                "last_name":data.get('g_last_name')}
    date_of_birth=data.get('dob')
    marital_status=data.get('marital')#single married or divorced default: single
    email=data.get('email')
    phone=data.get('phone')
    adhar=data.get('aadhar')
    pan=data.get('pan')
    permanent_address= {"house_no": data.get('house_no'),
              "city": data.get('city'),
              "pincode":data.get('pincode')
              }
    temporary_address= {"house_no": data.get('t_house_no'),
              "city": data.get('t_city'),
              "pincode":data.get('t_pincode')
              }
    account_holder= data.get('acc_holder') #boolean yes or no
    account_details={"account_no":data.get('acc_no'),
                     "branch":data.get('branch'),
                     "IFSC":data.get('ifsc')}
    occupation=data.get('occupation') #employed unemployed or student
    education=data.get('highest_level') #10 12 graduate etc
    
    
    #creating finger print
    fingerprint=crypto.add_finger_print(adhar)
    
    #Rechecking the birthdate and minor or major
    
    try:
        birth_date=datetime.strptime(date_of_birth,"%Y-%m-%d")
        today=datetime.now(timezone.utc)
        calculated_age=today.year-birth_date.year -((today.month, today.day)<(birth_date.month, birth_date.day))
        is_minor = calculated_age<18
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid or missing Date of Birth"}), 400
    
    
    metadata={
        "personal_details":{
            "name": full_name,
            "minor": is_minor,        # Storing the backend-verified status
            "marital_status": marital_status or "Single", # Fallback default
            "occupation": occupation,
            "education": education
        },
        "family_details":{
            "father": father_name,
            "mother": mother_name,
            "guardian": guardian_name if is_minor else None # Conditional profiling
        },
        "contact": {
            "email": email,
            "phone": phone
        },
        "addresses":{
            "permanent":permanent_address,
            "temporary":temporary_address
        },
        "system_linking": {
            "is_account_holder": account_holder,
            "account_details": account_details
        },
        "audit": {
            "submitted_at": today.isoformat(), # Reusing the timezone-aware 'today' object
            "kyc_status": "PENDING_VERIFICATION"
        }
    }
    
    #Encryption before adding to vault
    vault_data={
        "adhar_enc": crypto.encrypt_data(adhar),
        "pan_enc": crypto.encrypt_data(pan),
        "dob_enc": crypto.encrypt_data(date_of_birth),
        "fingerprint": fingerprint #to retrieve information on the basis of adhar
    }
    
    try:
        ref_id = db.save_kyc(metadata, vault_data)
        
        # Check if DB entry returned None (failure caught inside DatabaseManager)
        if not ref_id:
            return jsonify({"error": "Could not save record due to an internal database engine error"}), 500
            
        print(f"successfully saved with Reference ID: {ref_id}")
        return jsonify({
            "status": "success",
            "message": "KYC data secure vault entry created",
            "vault_ref": ref_id
        }), 201

    except Exception as e:
        print(f"Unexpected Route Error: {e}")
        return jsonify({"error": "An unexpected server event occurred processing your request"}), 500
    