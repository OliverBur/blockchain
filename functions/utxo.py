import os
import json

class UTXOManager:
    FILE_PATH = r'data\utxos.json'

    @staticmethod
    def load_utxos():
        if not os.path.exists(UTXOManager.FILE_PATH):
            return []
        with open(UTXOManager.FILE_PATH, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    
    @staticmethod
    def save_utxos(utxos):
        os.makedirs(os.path.dirname(UTXOManager.FILE_PATH), exist_ok=True)
        with open(UTXOManager.FILE_PATH, 'w') as f:
            json.dump(utxos, f, indent=4)

    @staticmethod
    def add_utxo(name, address, amount):
        utxos = UTXOManager.load_utxos()

        for user in utxos:
            if user['address'] == address:
                user['cantidad'].append(amount)
                break
        else:
            utxos.append({
                "name": name,
                "address": address,
                "cantidad": [amount]
            })

        UTXOManager.save_utxos(utxos)

    @staticmethod
    def delete_utxo(address, amount):
        utxos = UTXOManager.load_utxos()
        for user in utxos:
            if user['address'] == address:
                if amount in user['cantidad']:
                    user['cantidad'].remove(amount)
                    if not user['cantidad']:
                        utxos.remove(user)
                break
        UTXOManager.save_utxos(utxos)

    @staticmethod
    def spend_utxos(address, amount_needed):
        utxos = UTXOManager.load_utxos()
        for user in utxos:
            if user['address'] == address:
                user_utxos = sorted(user['cantidad'], reverse=True)
                selected = []
                accumulated = 0

                for utxo in user_utxos:
                    selected.append(utxo)
                    accumulated += utxo
                    if accumulated >= amount_needed:
                        break

                if accumulated < amount_needed:
                    return None  # Fondos insuficientes

                # Eliminar todos los UTXOs seleccionados
                for utxo in selected:
                    user['cantidad'].remove(utxo)

                # Agregar UTXO de cambio si existe
                change = accumulated - amount_needed
                if change > 0:
                    user['cantidad'].append(change)

                # Si ya no quedan UTXOs, eliminar al usuario
                if not user['cantidad']:
                    utxos.remove(user)

                UTXOManager.save_utxos(utxos)
                return selected

        return None

    @staticmethod
    def consolidate_utxos():
        utxos = UTXOManager.load_utxos()
        for user in utxos:
            total = sum(user['cantidad'])
            user['cantidad'] = [total] if total > 0 else []
        UTXOManager.save_utxos(utxos)

