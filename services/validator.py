import re

class KYCValidator:
    @staticmethod
    def validate_aadhar(number:str)->bool:
        pattern = r"^[2-9][0-9]{11}$"
        return bool(re.match(pattern, str(number)))
    
    @staticmethod
    def validate_pan(pan: str)-> bool:
        pattern = r"^[A-Z]{5}[0-9]{4}[A-Z]$"
        return bool(re.match(pattern, pan.upper()))