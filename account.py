#region imports
import streamlit as st
import pyrebase
import requests
#endregion

#region configDB
config = {
    "apiKey": "AIzaSyD4e11Z68I8wpAif9LOZQag0UcACEetBuw",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://console.firebase.google.com/project/software-pi/overview?hl=pt-br",
    "storageBucket": "console.firebase.google.com/project/software-pi/storage?hl=pt-br",
    "serviceAccount": "software-pi-ee3c8ccdcd27.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
#endregion

#region app
def app():
    st.markdown('<h1 style="text-align: center; margin-bottom: 50px;">Conta</h1>', unsafe_allow_html=True)
    
    if 'signedout' not in st.session_state:
        st.session_state.signedout = False
    if 'useremail' not in st.session_state:
        st.session_state.useremail = ''
    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    if 'idToken' not in st.session_state:
        st.session_state.idToken = None

    if st.session_state.signedout:
        st.write(f"Bem-vindo, {st.session_state.useremail}!")

        st.button("Sair", on_click=sign_out)
        st.button("Excluir conta", on_click=delete_account)

    else:
        login_register_screen()
#endregion

#region configLoginAoSair
def login_register_screen():
    st.markdown('<h1 style="text-align: center; margin-bottom: 50px;">Login / Cadastro</h1>', unsafe_allow_html=True)

    if st.session_state.show_register:
        st.subheader("Cadastro")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type='password')
        confirm_password = st.text_input("Confirmar Senha", type='password')

        if password != confirm_password:
            st.error("As senhas não coincidem! Digite novamente!")
        elif st.button("Cadastrar"):
            try:
                user = auth.create_user_with_email_and_password(email=email, password=password)
                st.success('Conta criada com sucesso! Você pode agora fazer login.')
                auth.send_email_verification(user['idToken'])
                st.session_state.show_register = False
            except Exception as e:
                st.warning(f'Erro ao criar conta: {e}')
    else:
        st.subheader("Login")
        email = st.text_input("E-mail")
        password = st.text_input("Senha", type='password')

        if st.button("Entrar"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                user = auth.refresh(user['refreshToken'])
                account_info = auth.get_account_info(user['idToken'])

                if account_info['users'][0]['emailVerified']:
                    st.session_state.signedout = True
                    st.session_state.useremail = email
                    st.session_state.idToken = user['idToken']
                    st.rerun()

                else:
                    st.warning('Verifique seu e-mail antes de fazer login.')
                    auth.send_email_verification(user['idToken'])

            except Exception as e:
                st.warning('Falha ao logar! Verifique suas credenciais.')

    if st.session_state.show_register:
        st.button("Já tem uma conta? Faça login!", on_click=toggle_register)
    else:
        st.button("Não tem uma conta? Registre-se!", on_click=toggle_register)

def toggle_register():
    st.session_state.show_register = not st.session_state.show_register

def sign_out():
    st.session_state.signedout = False
    st.session_state.useremail = ''
    st.session_state.idToken = None
    st.rerun()
#endregion

def delete_account():
    if st.session_state.idToken:
        try:
            # url = f"https://identitytoolkit.googleapis.com/v1/accounts:delete?key={config['apiKey']}"
            
            # headers = {"Content-Type": "application/json"}
            # payload = {"idToken": st.session_state.idToken}

            # response = requests.post(url, headers=headers, json=payload)
            
            # if response.status_code == 200:
            auth.delete_user_account(st.session_state.idToken)
            st.success("Conta deletada com sucesso!")
            sign_out()
            st.rerun()
            # else:
            #     st.error("Erro ao deletar a conta. Tente novamente.")
                
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
    else:
        st.warning("Nenhum usuário logado para deletar.")

if __name__ == "__main__":
    app()
