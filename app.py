# streamlit_app.py
import streamlit as st
from functions.users import User
from functions.utxo import UTXOManager
from functions.transaction import TransactionManager
from functions.blockchain import Blockchain, Block
import pandas as pd
import json

st.set_page_config(page_title="Blockchain App", layout="wide")

st.sidebar.title("Menú")
option = st.sidebar.radio("Selecciona una sección:", [
    "Inicio", "Usuarios", "Transacciones", "Minería", "Blockchain", "Balances"])

# INICIO
if option == "Inicio":
    st.title("Resumen General del Sistema")
    blockchain = Blockchain()
    st.metric("Número de Bloques", len(blockchain.chain))
    txs = TransactionManager.load_transactions()
    st.metric("Transacciones Totales", len(txs))
    st.metric("Recompensa de Minería", 3)

# USUARIOS
elif option == "Usuarios":
    st.title("Crear nueva Wallet")
    nombre = st.text_input("Nombre del nuevo usuario")
    if st.button("Crear Wallet") and nombre:
        user = User.create(nombre)
        st.success(f"Usuario {nombre} creado. Dirección: {user.address}")

    st.subheader("Usuarios existentes")
    with open("data/users.json") as f:
        users = json.load(f)
    df_users = pd.DataFrame(users)[["name", "address"]]
    st.dataframe(df_users)

# TRANSACCIONES
elif option == "Transacciones":
    st.title("Enviar Transacción")
    with open("data/users.json") as f:
        users = json.load(f)
    nombres = [u['name'] for u in users]

    sender = st.selectbox("Remitente", nombres)
    receiver = st.selectbox("Destinatario", nombres)
    monto = st.number_input("Monto", min_value=0.01, step=0.01)

    if st.button("Enviar"):
        success = TransactionManager.add_transaction(sender, receiver, monto)
        UTXOManager.consolidate_utxos()
        if success:
            st.success("Transacción exitosa")
        else:
            st.error("Error al realizar la transacción")

# MINERÍA
elif option == "Minería":
    st.title("Minería de Bloques")
    with open("data/users.json") as f:
        users = json.load(f)
    nombres = [u['name'] for u in users]
    nombre_minero = st.selectbox("Selecciona el minero", nombres)
    direccion_minero = next((u['address'] for u in users if u['name'] == nombre_minero), None)

    if st.button("Minar nuevo bloque"):
        blockchain = Blockchain()
        transactions = TransactionManager.load_transactions()
        if transactions:
            blockchain.add_block(transactions, miner_name=nombre_minero, miner_address=direccion_minero)
            TransactionManager.save_transactions([])
            st.success(f"Bloque minado exitosamente por {nombre_minero}")
        else:
            st.warning("No hay transacciones para minar")

# BLOCKCHAIN
elif option == "Blockchain":
    st.title("Cadena de Bloques")
    blockchain = Blockchain()
    data = []
    for b in blockchain.chain:
        data.append({
            "Índice": b.index,
            "Hash": b.hash[:12] + "...",
            "Anterior": b.previous_hash[:12] + "...",
            "Nonce": b.nonce,
            "# Transacciones": len(b.transactions),
            "Fecha": b.timestamp
        })
    df_blocks = pd.DataFrame(data)
    st.dataframe(df_blocks)

# BALANCES
elif option == "Balances":
    st.title("Saldos Actuales")
    utxos = UTXOManager.load_utxos()
    data = []
    for u in utxos:
        data.append({
            "Nombre": u["name"],
            "Dirección": u["address"],
            "Saldo": sum(u["cantidad"])
        })
    df = pd.DataFrame(data)
    st.dataframe(df)