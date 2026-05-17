from cryptography.fernet import Fernet
import config
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

class CryptoService:
    def __init__(self):
        self.key=config.secret_key
        self.cipher= Fernet(self.key)
        
        with open("keys/private_key.pem","rb") as f:
            self.private_key=serialization.load_pem_private_key(f.read(),password=None)
            
        with open("keys/public_key.pem","rb") as f:
            self.public_key=serialization.load_pem_public_key(f.read())
    
    #Encrypting the pan and adhar
    def encrypt_data(self, data:str)->str:
        return self.cipher.encrypt(data.encode()).decode()
    
    #Decrypting the pan and adhar
    def decrypt_data(self, token:str) -> str:
        return self.cipher.decrypt(token.encode()).decode()
    
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