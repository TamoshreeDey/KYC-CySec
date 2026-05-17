# Secure KYC Portal with Digital Signatures
A project which demonstrates how Digital signatures work in real life scenarios

This project is a high-security backend system designed to manage KYC (Know Your Customer) workflows. It utilizes a split-architecture design to ensure sensitive user data remains protected while maintaining full auditability through cryptographic signatures.

## Key Features
- **Decoupled Storage:** Sensitive ID data (like Aadhaar/PAN) is stored in a secure vault, linked to public metadata via unique Reference IDs.
- **End-to-End Encryption:** Uses the **Fernet** library for symmetric encryption of sensitive database fields.
- **Non-Repudiation:** Implements RSA-based digital signatures to ensure document integrity.

---

## Cryptography & Hashing
To ensure the highest level of security, the project uses a multi-layered cryptographic approach:

### 1. Hashing (SHA-256)
We use the **SHA-256** algorithm to create a unique digital "fingerprint" of the user's submission.
* **Purpose:** **Integrity.** Even a 1-bit change in the user's data will result in a completely different hash, making unauthorized modifications easy to detect.

### 2. Digital Signatures (RSA)
The system signs the SHA-256 hash using an **RSA Private Key**.
* **Purpose:** **Authenticity.** The signature proves the data was processed by this specific system and has not been tampered with since the moment of signing.
* **Workflow:**
    1. Data is hashed via SHA-256.
    2. The hash is encrypted with a Private Key to create a **Digital Signature**.
    3. Anyone with the Public Key can verify the signature to confirm the data's origin.

  ### 3. Data Encryption (Fernet)
While RSA handles the signatures, we use **Fernet** (from the Python `cryptography` library) to encrypt the actual sensitive data stored in our database.

* **Symmetric Encryption:** Fernet is a symmetric encryption method, meaning it uses the same secret key for both encryption and decryption.
* **Why Fernet?**
    * **Performance:** RSA is computationally "expensive" and slow for large data. Fernet is incredibly fast, making it ideal for encrypting database records or uploaded files.
    * **Built-in Integrity:** Fernet tokens are "authenticated." This means if someone tries to manually change the encrypted text in the database, the decryption will fail with an error. It includes a built-in HMAC (Hash-based Message Authentication Code).
    * **Standardized:** It uses **AES (Advanced Encryption Standard)** in CBC mode with a 128-bit key—the same standard used by governments and banks.


## Project Structure
```text
backend/
├── routes/           # API endpoints (KYC submission, validation)
├── services/         # Core logic (crypto.py, database.py, validator.py)
├── keygenerators_util/ # Utilities for RSA/Fernet key generation
├── keys/             # Secure storage for cryptographic keys
├── app.py            # Main Flask/FastAPI entry point
└── .env              # Configuration and secrets
```

## For database I used Mongodb and for backend I used Flask
