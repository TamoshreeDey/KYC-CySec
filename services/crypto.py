from cryptography.fernet import Fernet
import config
import json
import hashlib 
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
import re

class CryptoService:
    def __init__(self):
        self.key=config.secret_key
        self.cipher= Fernet(self.key)
        
        with open("keys/private_key.pem","rb") as f:
            self.private_key=serialization.load_pem_private_key(f.read(),password=None)
            
        with open("keys/public_key.pem","rb") as f:
            self.public_key=serialization.load_pem_public_key(f.read())
    
    #digital fingerprint
    def add_finger_print(self, data:str)-> str:
        clean_data = data.strip().upper() # Keeps formatting uniform (crucial for PAN)
        return hashlib.sha256(clean_data.encode('utf-8')).hexdigest()
    
    #Encrypting the pan and adhar
    def encrypt_data(self, data:str)->str:
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, token:str) -> str:
        val= self.cipher.decrypt(token.encode()).decode()
        
        # 1. Check for YYYY-MM-DD pattern using regex
        # ^\d{4}-\d{2}-\d{2}$ means: start with 4 digits, a hyphen, 2 digits, a hyphen, and end with 2 digits
        if re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            return "XXXX-XX-" + val[-2:]
            
        # 2. Check for other fields using length
        elif len(val) == 12:       # Aadhaar
            return 'XXXXXXXX' + val[-4:]
        elif len(val) == 10:       # PAN (Since it failed regex, it's alphanumeric PAN, not a date)
            return 'XXXXXX' + val[-4:]
        else:
            print("Length or format mismatch")
            return None
    
    #Signature generation
    def get_signature(self, metadata: dict, vault_data: dict)->bool:
        payload={"meta": metadata, "vault": vault_data}
        data_bytes=json.dumps(payload, sort_keys=True).encode()
        
        signature = self.private_key.sign(
            data_bytes,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256()
        )
        return signature.hex()
    
    #Signature verification
    def verify_signature(self, metadata: dict, vault_data: dict, signature_hex: str) -> bool:
        payload = {"meta": metadata, "vault": vault_data}
        data_bytes= json.dumps(payload, sort_keys=True).encode()
        
        try:
            self.public_key.verify(
                bytes.fromhex(signature_hex),
                data_bytes,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False