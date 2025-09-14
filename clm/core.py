# Copyright © 2025, Alexander Suvorov
import hmac
import hashlib


class HMAC_DRBG:
    def __init__(self, seed_material):
        self.K = b'\x00' * 32
        self.V = b'\x01' * 32
        self._update(seed_material)

    def _update(self, provided_data=None):
        data = provided_data if provided_data else b''
        self.K = hmac.new(self.K, self.V + b'\x00' + data, hashlib.sha256).digest()
        self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
        if provided_data:
            self.K = hmac.new(self.K, self.V + b'\x01' + data, hashlib.sha256).digest()
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()

    def generate(self, num_bytes):
        temp = b''
        while len(temp) < num_bytes:
            self.V = hmac.new(self.K, self.V, hashlib.sha256).digest()
            temp += self.V
        return temp[:num_bytes]


def encrypt_decrypt(data, key):
    return bytes([d ^ k for d, k in zip(data, key)])
