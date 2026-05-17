from flask import Flask, request, jsonify, Blueprint
from datetime import datetime, timezone
from services.validator import KYCValidator
from services.crypto import CryptoService
from services.database import DatabaseManager
import traceback

crypto=CryptoService()
kycval=KYCValidator()
db=DatabaseManager()

kyc_retrive= Blueprint('kyc_retrive',__name__)

@kyc_retrive.route("/retrive",methods=['POST'])
def retrive_kyc_data():
    try:
        data=request.json
        adhar=data.get('adhaar')
        adh_fp= crypto.add_finger_print(adhar)
        vault_ref=db.get_vault_ref(adh_fp)
        meta, secret, msg=db.get_full_kyc(vault_ref)
        res={
            "metadata": meta,
            "vault_data":{
                "adhar":crypto.decrypt_data(secret["adhaar"]),
                "pan":crypto.decrypt_data(secret["pan"]),
                "dob":crypto.decrypt_data(secret['dob'])
            },
            "verification": msg
        }
        return jsonify(res), 200
    except Exception as e:
        print(f"unexpected error: {e}")
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500