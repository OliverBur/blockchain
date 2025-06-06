from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import hashlib
import json
import os

class User:
    def __init__(self, private_key, name):
        self.name = name
        self.private_key = private_key
        self.public_key = private_key.public_key()
        self.address = self.calculate_address()

    def calculate_address(self):
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.X962,
            format=serialization.PublicFormat.UncompressedPoint
        )
        return hashlib.sha256(public_bytes).hexdigest()

    def to_dict(self):
        return {
            "name": self.name,
            "private_key": self.private_key.private_bytes(
                encoding=serialization.Encoding.DER,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ).hex(),
            "public_key": self.public_key.public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            ).hex(),
            "address": self.address
        }
    
    def sign_message(self, message):
        signature = self.private_key.sign(
            message.encode(),
            ec.ECDSA(hashlib.sha256())
        )
        return signature.hex()
    
    def verify_signature(self, message, signature):
        signature_bytes = bytes.fromhex(signature)
        try:
            self.public_key.verify(
                signature_bytes,
                message.encode(),
                ec.ECDSA(hashlib.sha256())
            )
            return True
        except Exception as e:
            print(f"Error al verificar la firma: {e}")
            return False

    @classmethod
    def create(cls, name=None):
        private_key = ec.generate_private_key(ec.SECP256K1())
        user = cls(private_key, name)

        file_path = r'data\users.json'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        users = []
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        users = data
                    else:
                        pass
                except json.JSONDecodeError:
                    print("Advertencia: users.json está vacío o mal formado. Se sobrescribirá.")

        if any(u["address"] == user.address for u in users):
            print("Usuario ya existe. No se agregó nuevamente.")
        else:
            users.append(user.to_dict())

        with open(file_path, 'w') as f:
            json.dump(users, f, indent=4)

        return user

    @classmethod
    def delete(cls, name):
        file_path = r'data\users.json'
        if not os.path.exists(file_path):
            print("No se encontró el archivo users.json.")
            return

        with open(file_path, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                print("Advertencia: users.json está vacío o mal formado.")
                return

        users = [u for u in users if u["name"] != name]

        with open(file_path, 'w') as f:
            json.dump(users, f, indent=4)

        print(f"Usuario {name} eliminado.")

    @classmethod
    def select(cls, name):
        file_path = r'data\users.json'
        if not os.path.exists(file_path):
            print("No se encontró el archivo users.json.")
            return None

        with open(file_path, 'r') as f:
            try:
                users = json.load(f)
            except json.JSONDecodeError:
                print("Advertencia: users.json está vacío o mal formado.")
                return None

        for user in users:
            if user["name"] == name:
                return {
                    "name": user["name"],
                    "address": user["address"],
                    "public_key": user["public_key"]
                }

        print(f"Usuario {name} no encontrado.")
        return None