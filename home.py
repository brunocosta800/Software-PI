import streamlit as st

def app():
  st.markdown('<h1 style="text-align: center;">Bem-vindo(a) <span style="color: #408CFF;">SmartTravel Insights</span></h1>', unsafe_allow_html=True)
  image_path = 'arquivos\DALL·E 2024-11-13 19.13.17 - A data science project visual representing the impact of national holidays on Brazilian tourism. The image should show a digital dashboard on a large .webp'
  st.image(image_path)