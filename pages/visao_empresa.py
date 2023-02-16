#Libraries
import haversine
from haversine import haversine, Unit
import folium
import plotly.express as px
import plotly.graph_objects as go

# Bibliotecas necessárias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static
import emoji

st.set_page_config(page_title='Visão Empresa', page_icon='📈', layout='wide')

#=======================================================================
#Funções
#=======================================================================
def clean_code( df ):
    """ Está função tem a responsabilidade de limpar o dataframe
    Tipos de limpezas:
    1. Remoção do dados NaN,
    2. Mudança do tipo da coluna de dados,
    3. Remoção dos espaçõs das variáveis de texto
    4. Formatação da coluna de data
    5. Limpeza da coluna de tempo (Remoção do texto da variável numérica)
    
    Input: DataFrame
    Output: DataFrame
    
    """
    
    # 1.Convertendo a coluna Delivery_person_Age para int
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype(int)
    
    linhas_selecionadas = (df['Road_traffic_density'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df['City'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df['Festival'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    
    # 2.Convertendo a coluna Delivery_person_Ratings para int
    linhas_selecionadas = (df['Delivery_person_Ratings'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype(float)
    
    # 3.Convertendo a coluna Order_Date para date time
    linhas_selecionadas = (df['Order_Date'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format= '%d-%m-%Y')
    
    # 4.Convertendo a coluna multiple_deliveries para int
    linhas_selecionadas = (df['multiple_deliveries'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)
    
    # 6. Removendo os espaços dentro de strings
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Weatherconditions'] = df.loc[:, 'Weatherconditions'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()
    
    #7. Limpamndo a coluna de time taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)
    
    return df 

def order_metric(df):
    cols = ['ID', 'Order_Date']
    # Selecao de linhas
    df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()
    fig = px.bar(df_aux, x= 'Order_Date', y='ID' )
    
    return fig

def trafic_order_share(df):
    df_aux = df.loc[:, ['ID',  'Road_traffic_density' ] ].groupby( 'Road_traffic_density' ).count().reset_index()
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!= "NaN", :]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie(df_aux, values='entregas_perc',names= 'Road_traffic_density')
    
    return fig

def trafic_order_city(df):
    df_aux = df.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density' ]).count().reset_index()
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return fig

def order_by_week(df):
    # Criar a coluna dia da semana
    df['week_of_day'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df.loc[:, ['week_of_day', 'ID']].groupby('week_of_day').count().reset_index()
    fig = px.line(df_aux, x='week_of_day', y='ID')
    return fig

def order_share_by_week(df):
    df_aux1 = df.loc[:,['ID', 'week_of_day']].groupby('week_of_day').count().reset_index()
    df_aux2 = df.loc[:,['Delivery_person_ID', 'week_of_day']].groupby('week_of_day').nunique().reset_index()
    df_aux = pd.merge(df_aux1, df_aux2, how='inner')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    fig = px.line(df_aux, x='week_of_day', y='order_by_deliver')
    return fig

def contry_maps(df):
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    map = folium.Map()
    
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], location_info[ 'Delivery_location_longitude' ]],popup=location_info[[ 'City', 'Road_traffic_density' ]]).add_to(map)
        
    folium_static( map, width=1024, height=600)
        
#------------------Início da estrutura lógica do código-----------------

#=======================================================================
# Import dataset
#=======================================================================

# Import dataset
data = pd.read_csv('csv/train.csv')
#Limpando dados
df = clean_code( data )


#===============================================================================
#Barra lateral - Streamlit
#===============================================================================

st.header('Marketplace - Visão Cliente')

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width= 200)

st.sidebar.markdown('# Cury Compay')
st.sidebar.markdown('## Fast Delivery en Town')
st.sidebar.markdown("""---""")


st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider('Até qual Valor', 
                                value=pd.datetime(2022, 4, 13),
                                min_value= pd.datetime(2022, 2, 11), 
                                max_value= pd.datetime(2022, 4, 6), 
                                format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do transito?',
                       ['Low', 'Medium', 'High', 'Jam'],
                       default= ['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Aline de Araújo')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#===============================================================================
#layout - Streamlit
#===============================================================================


tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric
        fig = order_metric(df)
        st.header('Orders by Day')
        st.plotly_chart(fig, use_container_width=True)   
                
    with st.container():
    
        col1, col2 = st.columns(2)
        with col1:
            fig = trafic_order_share(df)
            st.header('Traffic Order Share')
            st.plotly_chart(fig, use_container_width=True)    
                
        with col2:
            fig = trafic_order_city(df)
            st.header('Traffic Order City')
            st.plotly_chart(fig, use_container_width=True) 
            
with tab2:
    with st.container():
        fig = order_by_week(df)
        st.header('Order by Week')
        st.plotly_chart(fig, use_container_width=True)    
        
    with st.container():
        fig = order_share_by_week(df)
        st.header('Order Share by Week')
        st.plotly_chart(fig, use_container_width=True)
             
with tab3:
    st.header('Country Maps')
    contry_maps(df)