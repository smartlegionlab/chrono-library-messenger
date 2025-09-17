# Copyright © 2025, Alexander Suvorov
import hashlib
import hmac
import base64


class AuthManager:
    def __init__(self, db):
        self.db = db

    def generate_public_key(self, username: str, secret: str) -> str:
        key_material = f"{username}:{secret}".encode('utf-8')
        hmac_obj = hmac.new(b'clm-auth-key', key_material, hashlib.sha256)
        return base64.b64encode(hmac_obj.digest()).decode('utf-8')

    def verify_secret(self, username: str, secret: str, stored_public_key: str) -> bool:
        generated_key = self.generate_public_key(username, secret)
        return generated_key == stored_public_key
