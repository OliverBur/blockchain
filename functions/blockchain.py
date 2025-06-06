import hashlib
import json
import os
from datetime import datetime
from functions.utxo import UTXOManager

BLOCKCHAIN_FILE = "data/blocks.json"


class Block:
    def __init__(self, index, transactions, previous_hash, difficulty=3, timestamp=None, nonce=None, block_hash=None):
        self.index = index
        self.timestamp = timestamp or datetime.now().isoformat()
        self.transactions = transactions
        self.previous_hash = previous_hash

        if nonce is not None and block_hash is not None:
            self.nonce = nonce
            self.hash = block_hash
        else:
            self.nonce, self.hash = self.proof_of_work(difficulty)

    def calculate_hash(self, nonce):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, difficulty):
        prefix = "0" * difficulty
        nonce = 0
        while True:
            hash_attempt = self.calculate_hash(nonce)
            if hash_attempt.startswith(prefix):
                return nonce, hash_attempt
            nonce += 1

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data, difficulty=3):
        return Block(
            index=data["index"],
            transactions=data["transactions"],
            previous_hash=data["previous_hash"],
            difficulty=difficulty,
            timestamp=data["timestamp"],
            nonce=data["nonce"],
            block_hash=data["hash"]
        )


class Blockchain:
    def __init__(self, difficulty=3):
        self.chain = []
        self.difficulty = difficulty
        self.load_chain()

    def create_genesis_block(self):
        coinbase_tx = {
            "from": "coinbase",
            "to": "Fonsi",
            "amount": 1000,
            "type": "premine"
        }
        genesis_block = Block(0, [coinbase_tx], "0", self.difficulty)
        self.chain.append(genesis_block)
        self.save_chain()

    def add_block(self, transactions, miner_name="Miner", miner_address=None):
        reward_tx = {
            "from": "coinbase",
            "to": miner_name,
            "amount": 3,
            "type": "reward"
        }

        total_fees = sum(tx.get("fee", 0) for tx in transactions)
        reward_tx["amount"] += total_fees

        full_transactions = [reward_tx] + transactions
        previous_block = self.chain[-1]
        new_block = Block(previous_block.index + 1, full_transactions, previous_block.hash, self.difficulty)
        self.chain.append(new_block)
        self.save_chain()

        # Guardar recompensa en UTXOs para el minero solo si tenemos dirección
        if miner_address:
            UTXOManager.add_utxo(name=miner_name, address=miner_address, amount=reward_tx["amount"])
        else:
            # Si no tenemos dirección, no guardamos para evitar duplicados erróneos
            print("[Warning] No se guardó la recompensa: falta dirección del minero")

    def is_valid_chain(self):
        prefix = "0" * self.difficulty
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash(current.nonce):
                print(f"[Error] Hash incorrecto en el bloque {i}")
                return False

            if not current.hash.startswith(prefix):
                print(f"[Error] Hash no cumple PoW en el bloque {i}")
                return False

            if current.previous_hash != previous.hash:
                print(f"[Error] Hash anterior no coincide en el bloque {i}")
                return False
        return True

    def save_chain(self):
        with open(BLOCKCHAIN_FILE, "w") as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=4)

    def load_chain(self):
        if not os.path.exists(BLOCKCHAIN_FILE) or os.stat(BLOCKCHAIN_FILE).st_size == 0:
            self.create_genesis_block()
        else:
            with open(BLOCKCHAIN_FILE, "r") as f:
                block_data = json.load(f)
                self.chain = [Block.from_dict(b, self.difficulty) for b in block_data]

    def print_chain(self):
        for block in self.chain:
            print(json.dumps(block.to_dict(), indent=4))
