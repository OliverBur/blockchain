import os
import json
from datetime import datetime
from functions.utxo import UTXOManager

class TransactionManager:
    FILE_PATH = r'data\transactions.json'

    @staticmethod
    def load_transactions():
        if not os.path.exists(TransactionManager.FILE_PATH):
            return []
        with open(TransactionManager.FILE_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []

    @staticmethod
    def save_transactions(transactions):
        os.makedirs(os.path.dirname(TransactionManager.FILE_PATH), exist_ok=True)
        with open(TransactionManager.FILE_PATH, 'w') as f:
            json.dump(transactions, f, indent=4)

    @staticmethod
    def add_transaction(sender_name, receiver_name, amount):
        print(f"[DEBUG] Entró a add_transaction con sender: {sender_name}, receiver: {receiver_name}, amount: {amount}")
        utxos = UTXOManager.load_utxos()
        print(f"[DEBUG] UTXOs cargados: {utxos}")
        utxos = UTXOManager.load_utxos()

        # Buscar el usuario emisor por nombre
        sender_data = next((u for u in utxos if u['name'] == sender_name), None)
        print(f"[DEBUG] sender_data encontrado: {sender_data}")
        if not sender_data:
            print(f"[Error] El usuario emisor '{sender_name}' no tiene UTXOs registrados.")
            return False

        total_funds = sum(sender_data['cantidad'])
        print(f"[Info] Fondos disponibles para {sender_name}: {total_funds}")

        if total_funds < amount:
            print(f"[Error] Fondos insuficientes: {total_funds} disponibles, {amount} requeridos.")
            return False

        selected = UTXOManager.spend_utxos(sender_data['address'], amount)
        if selected is None:
            print(f"[Error] No se pudieron gastar los UTXOs necesarios.")
            return False

        print(f"[Info] UTXOs seleccionados: {selected}")

        receiver_data = next((u for u in utxos if u['name'] == receiver_name), None)
        receiver_address = receiver_data['address'] if receiver_data else receiver_name
        print(f"[Info] Dirección del receptor: {receiver_address}")

        UTXOManager.add_utxo(receiver_name, receiver_address, amount)
        print(f"[Info] Transacción de {sender_name} a {receiver_name} por {amount} registrada.")

        transactions = TransactionManager.load_transactions()
        transactions.append({
            "sender": sender_name,
            "receiver": receiver_name,
            "amount": amount,
            "timestamp": datetime.now().isoformat()
        })
        TransactionManager.save_transactions(transactions)
        return True
