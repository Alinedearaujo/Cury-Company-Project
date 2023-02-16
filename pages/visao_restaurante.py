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
import numpy as np

st.set_page_config(page_title='Visão Restaurante', page_icon='🥡', layout='wide')

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

def distance(df, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance_km'] = df.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
    
        avg_distance = np.round(df['distance_km'].mean(), 2)
    
        return avg_distance
    
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']

        df['distance'] = df.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
        
        avg_distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        
            # Avg_distance
        fig = go.Figure( data=[go.Pie(labels= avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
        return fig
        

def avd_std_delivery(df, festival, op):
    """ Está função calcula o tempo médio e o desvio padrão do tempo de entrega.
        Prâmentros:
            Input:
                - df: DataFrame com os dados necesários para o calculo
                - op: Tipo de operação que precisa ser calculado
                 'avg_time': Calcula o tempo médio
                 'std_time': Calcula o desvio padrão do tempo
            Output:
                - df: DaraFrame com 2 colunas e 1 linha
                """
    df_aux = df.loc[:,['Festival', 'Time_taken(min)']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, 'avg_time'], 2)
    
    return df_aux

def avg_std_time_graph(df):
    df_aux = df.loc[:,['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', 
                            x=df_aux['City'], 
                            y=df_aux['avg_time'], 
                            error_y= dict(type='data', array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
        
    return fig
                          

def avg_std_time_on_traffic(df):
    df_aux = df.loc[:,['City', 'Road_traffic_density', 'Time_taken(min)']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            
    df_aux.columns = ['avg_time', 'std_time']
    
    df_aux = df_aux.reset_index()
    df_aux.head()
    
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', 
                      color='std_time', color_continuous_scale='RdBu', 
                              color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig
                          
#============================================================================
# Import datasett
#===============================================================================

data = pd.read_csv('csv/train.csv')
df = clean_code( data )


#===============================================================================
#Barra lateral - Streamlit
#===============================================================================

st.header('Marketplace - Visão Restaurante')

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
st.sidebar.markdown('### Powered by Aline de Araújo')

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
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = df.loc[:, ['Delivery_person_ID', 'ID']].groupby('Delivery_person_ID').nunique().count()
            st.metric('Entregadores únicos', delivery_unique )
            
        with col2:
            avg_distance = distance(df, fig=False)
            st.metric('A distancia média', avg_distance)
            
        with col3:
            df_aux = avd_std_delivery(df, 'Yes', 'avg_time')
            col3.metric('Tempo médio', df_aux)
            
        with col4:
            df_aux = avd_std_delivery(df, 'Yes', 'std_time')
            col4.metric('STD entrega', df_aux)
            
        with col5:
            df_aux = avd_std_delivery(df, 'No', 'avg_time')
            col5.metric('Tempo médio', df_aux)
            
        with col6:
            df_aux = avd_std_delivery(df, 'No', 'std_time')
            col6.metric('STD entrega', df_aux)
            
    with st.container():
        st.markdown("""___""")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.title('Tempo médio de entrega por cidade')
            fig = avg_std_time_graph(df)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.title('Distribuição da distância')
            df_aux = df.loc[:,['City', 'Type_of_order', 'Time_taken(min)']].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})

            df_aux.columns = ['avg_time', 'std_time']

            df_aux = df_aux.reset_index()
            st.dataframe(df_aux)
        
    with st.container():
        st.title('Distribuição do tempo')
                
        col1, col2 = st.columns(2)
        
        with col1:
            fig = distance(df, fig=True)
            st.plotly_chart(fig, use_container_width=True)
           
                
        with col2:
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart(fig, use_container_width=True)       