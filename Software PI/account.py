import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
import pyrebase

# cred = credentials.Certificate('software-pi-ee3c8ccdcd27.json')
# firebase_admin.initialize_app(cred)

config = {
  "apiKey": "AIzaSyD4e11Z68I8wpAif9LOZQag0UcACEetBuw",
  "authDomain": "projectId.firebaseapp.com",
  "databaseURL": "https://console.firebase.google.com/project/software-pi/overview?hl=pt-br",
  "storageBucket": "https://console.firebase.google.com/project/software-pi/storage?hl=pt-br",
  "serviceAccount": "software-pi-ee3c8ccdcd27.json"
}

firebase = pyrebase.initialize_app(config)

def app():
    st.title("Login / Cadastro")

    if 'show_register' not in st.session_state:
        st.session_state.show_register = False

    if st.button("Registrar"):
        st.session_state.show_register = True
    if st.button("Voltar para Login"):
        st.session_state.show_register = False

    if st.session_state.show_register:
        st.subheader("Cadastro")
        email = st.text_input("E-mail")
        username = st.text_input("Usuário")
        password = st.text_input("Senha", type='password')
        confirm_password = st.text_input("Confirmar Senha", type='password')

        if password != confirm_password:
            st.error("As senhas não coincidem! Digite novamente!")
        elif username == "":
            st.error("O usuário não pode estar vazio!")
        elif st.button("Cadastrar"):
            user = auth.create_user(email=email, password=password, uid=username)
            st.success('Conta criada com sucesso! Por favor, logue usando seu e-mail e senha.')

    else:
        st.subheader("Login")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type='password')

        if st.button("Entrar"):
            try:
                user = auth.signi
                st.success('Login feito com sucesso!')
            except Exception as e:
                st.warning('Falha ao logar!')

if __name__ == "__main__":
    app()
