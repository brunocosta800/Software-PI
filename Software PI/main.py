import streamlit as st
from streamlit_option_menu import option_menu
import home
import dashboard
import account
import about

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

  def run():
        with st.sidebar:        
            app = option_menu(
                menu_title='SmartTravel Insights',
                options=['Home','Dashboard','Conta','Sobre o Projeto'],
                icons=['house-fill','file-earmark-text','person-circle','info-circle-fill'],
                menu_icon='airplane',
                default_index=0,
                styles={
                    "container": {"padding": "5!important","background-color":'black'},
        "icon": {"color": "white", "font-size": "23px"}, 
        "nav-link": {"color":"white","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "blue"},
        "nav-link-selected": {"background-color": "#408CFF"},}
                
                )
        if app == 'Home':
            home.app()
        if app == 'Dashboard':
            dashboard.app()
        if app == 'Conta':
            account.app()
        if app == 'Sobre o Projeto':
            about.app()

  run()
