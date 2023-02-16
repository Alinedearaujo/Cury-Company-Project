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
import streamlit as st

st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout='wide')

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

def top_delivers(df, top_asc):
    df1 = df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)' ]].groupby(['City', 'Delivery_person_ID']).max().sort_values(['City', 'Time_taken(min)'], ascending= top_asc).reset_index()
    
    df_aux1 = df1.loc[df1['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df1.loc[df1['City'] == 'Urban', :].head(10)
    df_aux3 = df1.loc[df1['City'] == 'Semi-Urban', :].head(10)
    
    df2 = pd.concat([df_aux1, df_aux2, df_aux3]).reset_index()
    
    return df
#===============================================================================
# Import datasett
#===============================================================================

data = pd.read_csv('csv/train.csv')
df = clean_code( data )

#===============================================================================
#Barra lateral - Streamlit
#===============================================================================

st.header('Marketplace - Visão Entregadores')

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

weatherconditions_options = st.sidebar.multiselect('Quais as condições climáticas?',
                       ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
                       default= ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Powered by Aline de Araújo')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#Filtro de condições climáticas
linhas_selecionadas = df['Weatherconditions'].isin(weatherconditions_options)
df = df.loc[linhas_selecionadas, :]

#===============================================================================
#layout - Streamlit
#===============================================================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap='large')
        
        with col1:
            #st.subheader('Maior idade')
            # Maior idade dos entregadores
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric(' Maior Idade', maior_idade)

            
        with col2:
            #st.subheader('Menor idade')
            # Menor idade dos entregadores
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric(' Menor idade', menor_idade)
            
        with col3:
            #st.subheader('Melhor condição de veículos')
            # condições dos veiculos
            melhor_condicao = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor_condicao)

        with col4:
            #st.subheader('Pior condição de veículos')
            # condições dos veiculos
            pior_condicao = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns( 2 )
        
        
        with col1:
            st.markdown( '##### Avalicao medias por Entregador' )
            df_avg_ratings_per_deliver = ( df.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                              .groupby( 'Delivery_person_ID' )
                                              .mean()
                                              .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
            
        with col2:
            st.markdown(' ##### Avalisção média por transito')
            df_avg_std_rating_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density' ] ].groupby('Road_traffic_density').agg({'Delivery_person_Ratings': ['mean', 'std']}))

            df_avg_std_rating_by_traffic.columns = ['delirery_mean', 'delirery_std']

            df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.markdown(' ##### Avalisção média por clima')
            df_avg_std_rating_by_wather = df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings': ['mean', 'std']})

            df_avg_std_rating_by_wather.columns = ['delirery_mean', 'delirery_std']

            df_avg_std_rating_by_wather.reset_index()
            st.dataframe(df_avg_std_rating_by_wather)
           
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
                
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top entregadores mais rápidos')
            df2 = top_delivers(df, top_asc=True)
            st.dataframe(df2)
                        
        with col2:
            st.subheader('Top entregadores mais lentos')
            df2 = top_delivers(df, top_asc=False)
            st.dataframe(df2)
            
                