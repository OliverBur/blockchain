from functions.utxo import UTXOManager
from functions.transaction import TransactionManager
from functions.blockchain import Blockchain
from functions import users

def main():
    user1 = users.User.select("Fonsi")
    user2 = users.User.select("Oliver")

    # Agregar UTXOs
    UTXOManager.add_utxo(user1['name'], user1['address'], 50)
    UTXOManager.add_utxo(user2['name'], user2['address'], 20)

    # Realizar transacción
    TransactionManager.add_transaction(user1['name'], user2['name'], 40)
    UTXOManager.consolidate_utxos()

    # Cargar transacciones
    transactions = TransactionManager.load_transactions()

    # Crear blockchain y agregar bloque minado
    blockchain = Blockchain(difficulty=3)
    blockchain.add_block(transactions, miner_name=user1['name'], miner_address=user1['address'])
    UTXOManager.consolidate_utxos()

    # Verificar cadena y mostrar
    print("Blockchain válida:", blockchain.is_valid_chain())


if __name__ == "__main__":
    main()