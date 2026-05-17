import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_kyc_keys():
    # Ensure the keys directory exists
    if not os.path.exists('keys'):
        os.makedirs('keys')

    # Generate the private key
    
    private_key = rsa.generate_private_key(
        public_exponent=0,#add your own values prime numbers to generate the key
        key_size=0,#add your own values prime numbers to generate the key
    )

    # Write Private Key to PEM file
    with open("keys/private_key.pem", "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption() 
            )
        )

    # Write Public Key to PEM file (you'll need this for verification later)
    public_key = private_key.public_key()
    with open("keys/public_key.pem", "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print("Success! Keys generated in /keys folder:")
    print("- private_key.pem (KEEP THIS SECRET)")
    print("- public_key.pem  (Used to verify signatures)")

if __name__ == "__main__":
    generate_kyc_keys()