import uuid
from config import db_name, vault_col, kyc_col
from bson.objectid import ObjectId
from services.crypto import CryptoService

crypto=CryptoService()

class DatabaseManager:
    @staticmethod
    def save_kyc(metadata: dict, encrypted_data: dict):
        try:
            
            ref_id=str(uuid.uuid4())
            
            metadata["vault_ref"]=ref_id #primary key
            
            
            vault_entry={
                "vault_ref": ref_id, #foreign key
                "adhaar": encrypted_data.get("adhar_enc"),
                "pan": encrypted_data.get("pan_enc"),
                "dob":encrypted_data.get("dob_enc")
            }
            
            signature= crypto.get_signature(metadata, vault_entry)
            
            metadata["signature"]=signature
            
            print(type(metadata))
            
            db_name[kyc_col].insert_one(metadata)
            #go to db_name then enter kyc. inside kyc insert the metadata
            db_name[vault_col].insert_one(vault_entry)
            
            return ref_id
        except Exception as e:
            print(f"DB Error:{e}")
            return None
        
    @staticmethod
    def get_full_kyc(vault_ref: str):
        meta=db_name[kyc_col].find_one({"vault_ref": vault_ref})
        secret = db_name[vault_col].find_one({"vault_ref": vault_ref})
        
        if not meta or not secret:
            return None,None, "Records not found"
        
        stored_sig=meta.get("signature")
        
        og_meta={k: v for k, v in meta.items() if k not in ["signature","_id"]}
        # Here we are removing the signature field first and getting the original data which was present. 
        #Because if we dont do it then we will be creating a signature for the data+signature which will result 
        # in mismatch. we verify the signature only with the original data not og data+sig.
        
        clean_secret = {k: v for k, v in secret.items() if k != "_id"}
        
        is_valid=crypto.verify_signature(og_meta, clean_secret, stored_sig)
        
        if not is_valid:
            return None, None, "Tampering Detected! data integrity Compromised."
        return meta, secret, "Verified ok"