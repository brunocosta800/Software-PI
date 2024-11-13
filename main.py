#region imports
import streamlit as st
import subprocess
from streamlit_option_menu import option_menu
import home
import account
import about
import pyrebase
#endregion

#region configDB
config = {
    "apiKey": "AIzaSyD4e11Z68I8wpAif9LOZQag0UcACEetBuw",
    "authDomain": "projectId.firebaseapp.com",
    "databaseURL": "https://console.firebase.google.com/project/software-pi/overview?hl=pt-br",
    "storageBucket": "https://console.firebase.google.com/project/software-pi/storage?hl=pt-br",
    "serviceAccount": "software-pi-ee3c8ccdcd27.json"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
#endregion 

#region configPageMain
st.set_page_config(
    page_title="SmartTravel Insights"
)

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, function):
        self.apps.append({
            "title": title,
            "function": function
        })

    def run(self):
        if 'signedout' not in st.session_state or not st.session_state.signedout:
            login_screen()
        else:
            self.show_app_menu()

    def show_app_menu(self):
        with st.sidebar:
            app = option_menu(
                menu_title='SmartTravel Insights',
                options=['Home', 'Dashboard', 'Conta', 'Sobre o Projeto'],
                icons=['house-fill', 'file-earmark-text', 'person-circle', 'info-circle-fill'],
                menu_icon='airplane',
                default_index=0,
                styles={
                    "container": {
                        "padding": "5!important", 
                        "background-color": 'black'
                    },
                    "icon": {
                        "color": "white", 
                        "font-size": "23px"
                    },
                    "nav-link": {
                        "color": "white", 
                        "font-size": "20px", 
                        "text-align": "left", 
                        "margin": "0px", 
                        "--hover-color": "blue"
                    },
                    "nav-link-selected": {
                        "background-color": "#408CFF"
                    },
                    "menu-title": {
                        "color": "white", 
                        "font-size": "24px"
                    }
                }
            )

        if app == 'Home':
            home.app()
        if app == 'Dashboard':
            self.run_dashboard()
        if app == 'Conta':
            account.app()
        if app == 'Sobre o Projeto':
            about.app()

    def run_dashboard(self):
        """ Inicia o servidor Dash em um subprocesso """
        subprocess.Popen(["python", "dashboard.py"])

        st.markdown(
            """
            <h1 style="text-align: center;">Dashboard</h1>
            <iframe src="http://localhost:8051" width="100%" height="600px"></iframe>
            """, 
            unsafe_allow_html=True
        )
#endregion 

#region configLoginAoIniciar
def login_screen():
    st.markdown('<h1 style="text-align: center; margin-bottom: 50px;">Login / Cadastro</h1>', unsafe_allow_html=True)

    if 'show_register' not in st.session_state:
        st.session_state.show_register = False
    
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
                st.rerun()
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
                st.session_state.signedout = True
                st.session_state.useremail = email
                st.rerun()
            except Exception as e:
                st.warning('Falha ao logar! Verifique suas credenciais.')

    if st.session_state.show_register:
        st.button("Já tem uma conta? Faça login!", on_click=toggle_register)
    else:
        st.button("Não tem uma conta? Registre-se!", on_click=toggle_register)

def toggle_register():
    st.session_state.show_register = not st.session_state.show_register
    
#endregion 

if __name__ == "__main__":
    app = MultiApp()
    app.run()
