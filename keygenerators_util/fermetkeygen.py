#Generate the encryption key and store it in your env file
#to be used on adhar and pan for encryption

from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())