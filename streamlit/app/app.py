import streamlit as st
from pymongo import MongoClient

# Configurações iniciais
client = MongoClient("mongodb://root:mongo@mongo_service:27017/")
db = client['your_database']
collection = db['your_collection']

st.title("Relatórios de Dados")

# Mostra dados da coleção
data = list(collection.find())
st.write(data)
