import streamlit as st
from PIL import Image
import emoji

st.set_page_config(
    page_title = 'Home',
    page_icon = '🎲', layout='wide')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width= 200)

st.sidebar.markdown('# Cury Compay')
st.sidebar.markdown('## Fast Delivery en Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown("""
Groenth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.

### Como utilizar esse Growth Dashboard?

### Visão da empresa

Visão Gerencial: Métricas gerais de comportamento.
Visão Tática: Indicadores semanais de comportamento.
Visão Geográfica: Insights de geolocalização.
    
### Visão Entregador

Acompanhamento dos indicadores semanais de crecimento.
    
### Visão Restaurante

Indicadores semanais de crescimento dos restaurantes.
   
   
### Ask for Help

Time de Data Scienceno Discord
    Aline_Araujo#6290
""")

    
