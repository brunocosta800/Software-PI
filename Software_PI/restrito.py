import streamlit as st

def app():
    # Verifica se o usuário está autenticado
    if 'signedout' not in st.session_state or not st.session_state.signedout:
        st.warning("Você precisa estar logado para acessar este conteúdo.")
        st.stop()  # Impede que o restante do conteúdo seja carregado

    # Se o usuário estiver autenticado, exibe o conteúdo restrito
    st.title("Bem-vindo à Área Privada!")
    st.write(f"Usuário autenticado: {st.session_state.useremail}")
    st.button('Sair', on_click=sign_out)

def sign_out():
    # Limpa o estado de sessão e retorna ao login
    st.session_state.signedout = False
    st.session_state.useremail = ''
    st.rerun()  # Recarrega a página e vai de volta para o script de login

if __name__ == "__main__":
    app()
