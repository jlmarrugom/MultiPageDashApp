from dash.dependencies import Input, Output

from app import app
import numpy as np
import pandas as pd
import folium

import plotly.graph_objects as go
######################################################
#Funciones
######################################################
#Here are all the functions used in the app

def pre_processing(df,nombre):
    """
    Recibe un DataFrame y lo entrega 
    listo para la aplicación.
    nombre: pcr, sero, anim, mur, air
    """
    if nombre=='pcr':
        df['RESULTADO PCR'] = df['RESULTADO PCR'].replace({'2':0,
                                                                'POSITIVO':1,
                                                                'NEGATIVO':0,
                                                                'Pendiente':np.nan,
                                                                'NO LLEGO MUESTRA ':np.nan}).astype(float)
        df['EDAD'] = df['EDAD'].replace({'NO REGISTRA':np.nan}).astype(float).astype('Int16')
        df['MUNICIPIO'] = df['MUNICIPIO'].astype(object).replace({1:'Lorica',
                                                                    2:'Planeta Rica',
                                                                    3:'Tierralta',
                                                                    4:'Sahagun',
                                                                    5:'Montelibano',
                                                                    6:'Montería'})                                           
    elif nombre=='sero':
        df['MUNICIPIO'] = df['MUNICIPIO'].astype(object).replace({1:'Lorica',
                                                                    2:'Planeta Rica',
                                                                    3:'Tierralta',
                                                                    4:'Sahagun',
                                                                    5:'Montelibano',
                                                                    6:'Montería'}) 
        df['RESULTADO SEROLOGIA'] = df['RESULTADO SEROLOGIA'].replace({'2':0,
                                                                'POSITIVO':1,
                                                                'NEGATIVO':0,
                                                                'Pendiente':np.nan,
                                                                'NO LLEGO MUESTRA ':np.nan}).astype(float)
    elif nombre=='mur':
        df['Coordenadas'] = df['lat'].astype(str) + ', '+df['lon'].astype(str)
        df['MUNICIPIO'] = df['Lugar']
    return df

def module_selection(data,number):
  """
  Selector de modulo de los datos. Entrega DataFrame.
  1. Info Básica.
  2. Actitudes con enfermos o asintomáticos con COVID-19
  3. Prácticas sobre COVID-19.
  4. Percepción sobre la pandemia.				
  5. Situación laboral y social.				
  6. Conocimiento sobre COVID-19.				
  """
  if number==1:
    return data.loc[:,'COD':'EN CASO DE HABER TOMADO MEDICAMENTOS CUÁLES TOMÓ?']
  elif number==2:
    return data.loc[:,'ALGUIEN EN LA FAMILIA O USTED A SIDO REPORTADO COMO ENFERMO DE COVID-19?':'USAN MASCARILLAS O CARETAS DENTRO DE LA VIVIENDA']
  elif number==3:
    return data.loc[:,'DURANTE LA PANDEMIA ME HE QUEDADO EN CASA':'OTRO CUAL?']
  elif number==4:
    return data.loc[:,'YO CREO QUE?':'ME HABRIA AISLADO VOLUNTARIAMENTE']
  elif number==5:
    return data.loc[:,'PERDÍ MI TRABAJO':'1 CAMBIÉ TENGO MÁS INGRESOS']
  elif number==6:
    return data.loc[:,'¿LA COVID -19 ES?':'DISTANCIAMIENTO SOCIAL']
  else:
    return data.loc[:,'CÓDIGO':]

def apilado(datos,prueba,agrupacion):
    """
    Esta función recibe un set de datos DataFrame, 
    el tipo de Prueba PCR o Serologia, y la variable 
    sobre la que se desean agrupar los datos.
    Retorna un grafico de barras apilado.
    """
    #mapear los datos a numero
    # datos[agrupacion]=datos[agrupacion].astype(int)
    datos[prueba] = datos[prueba].replace({'POSITIVO':1,
                                            'NEGATIVO':0})
    #print(datos[prueba].value_counts())
    #agrupación
    positivos = datos[[prueba,agrupacion]].loc[datos[prueba]==1].groupby(agrupacion).count()
    negativos = datos[[prueba,agrupacion]].loc[datos[prueba]==0].groupby(agrupacion).count()

    positivos.rename(columns={prueba:'Positivos'},inplace=True)
    negativos.rename(columns={prueba:'Negativos'},inplace=True)

    tabla = pd.concat([positivos, negativos],axis = 1)

    #Creación de la figura
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x = tabla.index,
        y = tabla['Positivos'],
        name='Positivos',
        marker_color='rgb(26, 118, 255)'
    ))
    fig.add_trace(go.Bar(
        x = tabla.index,
        y = tabla['Negativos'],
        name='Negativos',
        marker_color='rgb(55, 83, 109)'
    ))
    fig.update_layout(
    title='Distribución de Pruebas por Edades',
    xaxis_tickfont_size=14,
    yaxis=dict(
        title='Conteo (Individuos)',
        titlefont_size=16,
        tickfont_size=14,
    ),
    legend=dict(
        x=0,
        y=1.0,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ))

    fig.update_layout(barmode='stack')
    return fig
                                
def donut_plot(bats,bw):
    """
    bw: string con nombre de la columna.
    Recibe un Dataframe y la columna bw,
    agrupa los datos respecto a bw, hace el conteo
    y grafica una donut.
    """
    bats = bats[['Conteo',bw]].groupby(bw).sum().sort_values(by='Conteo',ascending=False)

    labels = bats.index
    values = bats['Conteo']

    fig = go.Figure(
        data=[go.Pie(
            labels=labels,
            values=values,
            hole=.5
        )]
    )
    return fig



def radial_plot(df,prueba):
    """
    Recibe un dataframe con datos de los síntomas de los pacientes
    y grafica un gráfico radial donde cada linea correspone al 
    promedio de sintomas por cada municipio.

    prueba: pcr, sero.
    """
    if prueba=='sero':
        data = module_selection(df,1).copy(deep=True) #Info básica
        data.loc[:,'HA ESTADO ENFERMO A HA TENIDO SÍNTOMAS LOS ÚLTIMOS TRES MESES':'DIARREA'] = data.loc[:,'HA ESTADO ENFERMO A HA TENIDO SÍNTOMAS LOS ÚLTIMOS TRES MESES':'DIARREA'].replace({2:0,3:np.nan}) #Cambio según la convención 0: No, 1 Sí
        #Seleccionamos sólo personas con síntomas:
        data = data.loc[data['HA ESTADO ENFERMO A HA TENIDO SÍNTOMAS LOS ÚLTIMOS TRES MESES']!=0].dropna() #los nan bajan el promedio
        data = data.groupby('MUNICIPIO').mean() #Agrupamos el promedio de cada síntoma por municipio
        #Radial plot
        data = data.loc[:,'FIEBRE Ó ESCALOFRIOS':'DIARREA']
    else:
        data = df.copy(deep=True)
        data.loc[:,'FIEBRE Ó ESCALOFRIOS':'DIARREA'] = data.loc[:,'FIEBRE Ó ESCALOFRIOS':'DIARREA'].replace({2:0,3:np.nan}) #Cambio según la convención 0: No, 1 Sí
        #Seleccionamos sólo personas con síntomas:
        data = data.loc[data['RESULTADO PCR']!=0].dropna() #los nan bajan el promedio
        data = data.groupby('MUNICIPIO').mean() #Agrupamos el promedio de cada síntoma por municipio
        #Radial plot
        data = data.loc[:,'FIEBRE Ó ESCALOFRIOS':'DIARREA']

    # data = data.reset_index()


    categories = ['FIEBRE Ó ESCALOFRIOS','TOS','DIFICULTAD PARA RESPIRAR','FATIGA','DOLORES MUSCULARES Y CORPORALES',
                'DOLOR DE CABEZA','PERDIDAD DEL OLFATO O DEL GUSTO','DOLOR DE GARGANTA',
                'CONGESTION DE LA NARIZ','NÁUSEAS O VÓMITOS','DIARREA']

    fig = go.Figure()
    for i in range(len(data)):

        fig.add_trace(go.Scatterpolar(
            r=data.iloc[i],
            theta=categories,
            name=str(data.index[i])
        ))
    # fig.add_trace(go.Scatterpolar(
    #     r=data.iloc[1],
    #     theta=categories,

    #     name='Planeta Rica'
    # ))
    # fig.add_trace(go.Scatterpolar(
    #     r=data.iloc[2],
    #     theta=categories,
    #     name='Montelibano'
    #     ))
    # fig.add_trace(go.Scatterpolar(
    #     r=data.iloc[3],
    #     theta=categories,
    #     name='Tierralta'
    #     ))
    # fig.add_trace(go.Scatterpolar(
    #     r=data.iloc[4],
    #     theta=categories,
    #     name='Monteria'
    #     ))
    # fig.add_trace(go.Scatterpolar(
    #     r=data.iloc[5],
    #     theta=categories,
    #     name='Sahagún'
    #     ))

    fig.update_layout(
    polar=dict(
        radialaxis=dict(
        visible=True,
        range=[0, 1]
        )),
    showlegend=True
    )

    fig.update_layout(
        title={
            'text': "Sintomas por Municipio",
            'y':0.95,
            'x':0.45,
            'xanchor': 'center',
            'yanchor': 'top'}
        # legend=dict(
        # yanchor="top",
        # y=0.99,
        # xanchor="left",
        # x=0.10)
    )

    #fig.show()
    return fig


def mun_to_coord(full_ser):
    """
    Recibe un Dataframe con municipios,
     añade sus coordenadas
    y regresa un Dataframe.
    """
    # try: #Para el dataset de Murcielagos
    #     full_ser['MUNICIPIO'] = full_ser['Lugar']
    # except:
    #     pass

    full_ser['lat']=0
    full_ser['lon']=0

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Montería'] = 8.7558921
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Montería'] = -75.887029

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Lorica'] = 9.2394583
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Lorica'] = -75.8139786

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Planeta Rica'] = 8.4076739 
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Planeta Rica'] = -75.5840456 

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Tierralta'] = 8.1717342
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Tierralta'] = -76.059376

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Sahagun'] = 8.9472964
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Sahagun'] = -75.4434972

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Montelibano'] = 7.9800534
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Montelibano'] = -75.4167198

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='Cereté'] = 8.8852282
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='Cereté'] = -75.7922421

    full_ser['lat'].loc[full_ser['MUNICIPIO']=='San Antero'] = 9.373016
    full_ser['lon'].loc[full_ser['MUNICIPIO']=='San Antero'] = -75.7595056


    return full_ser

def table_prueba(pat_df,prueba):
    """
    Genera la tabla necesaria para el mapa
    Prueba: string Tipo de prueba, Serologia o PCR, son sets de datos distintos
    Entrega una tabla agrupada por municipio con conteo de pruebas y
    No de Positivos
    """
    df = pat_df.copy(deep=True)
    df = df[['lat','lon','MUNICIPIO']].groupby('MUNICIPIO').max()

    if prueba=='PCR':
        # df = pat_df[pat_df['RESULTADO PCR']=='POSITIVO'] 
        # df = df.dropna()
        # max_amount = float(df['export_val'].max())
        df = df.merge(pat_df[['RESULTADO PCR','MUNICIPIO']].loc[pat_df['RESULTADO PCR']==1].groupby(['MUNICIPIO']).count() ,how='outer',on='MUNICIPIO')
        df = df.merge(pat_df[['RESULTADO PCR','MUNICIPIO']].groupby(['MUNICIPIO']).count() ,how='inner',on='MUNICIPIO')

        #df = df.merge(pat_df[['RESULTADO PCR','MUNICIPIO']].loc[pat_df['RESULTADO PCR']=='POSITIVO'].groupby(['MUNICIPIO']).agg(lambda x:x.value_counts().index[0])
        df = df.rename(columns={'RESULTADO PCR_x':'POSITIVOS PCR',
                                'RESULTADO PCR_y':'No DE PRUEBAS PCR'})
        df = df.reset_index()
    else:
        df = df.merge(pat_df[['RESULTADO SEROLOGIA','MUNICIPIO']].loc[pat_df['RESULTADO SEROLOGIA']==1].groupby(['MUNICIPIO']).count() ,how='outer',on='MUNICIPIO')
        df = df.merge(pat_df[['RESULTADO SEROLOGIA','MUNICIPIO']].groupby(['MUNICIPIO']).count() ,how='inner',on='MUNICIPIO')

        #df = df.merge(full_ser[['RESULTADO PCR','MUNICIPIO']].loc[full_ser['RESULTADO PCR']=='POSITIVO'].groupby(['MUNICIPIO']).agg(lambda x:x.value_counts().index[0])
        df['VULNERABILIDAD (%)'] = round(100*(1-(df['RESULTADO SEROLOGIA_x']/df['RESULTADO SEROLOGIA_y'])))
        df = df.rename(columns={'RESULTADO SEROLOGIA_x':'POSITIVOS SEROLOGIA',
                                'RESULTADO SEROLOGIA_y':'No DE PRUEBAS SEROLOGIA'})
        df = df.reset_index()
    return df

def mapping_df(full_ser,prueba):
    """
    Recibe un Dataframe con Coordenadas y lo grafica
    en un mapa. retorna un html para usar con Iframe.

    Prueba es el tipo de prueba, Serologia o PCR
    """
    df = table_prueba(full_ser, prueba)
    # print(df.head())
    #Mapa:

    folium_hmap = folium.Figure(width=500, height=500)
    m = folium.Map(location=[8.3344713,-75.6666238],
                            width='100%',
                            height='100%',
                            zoom_start=8,#Por defecto es 10
                            tiles="OpenStreetMap" #OpenSteetMap ,Stamen Toner(Terrain, Watercolor)
                            ).add_to(folium_hmap)

    data = df
    if prueba=='Serologia':
        for i in range(0,len(data)):
            html = f"""
                    <head>
                        <link rel="stylesheet" href="https://codepen.io/chriddyp/pen/dZVMbK.css">
                    <head>
                    <h6> {data.iloc[i]['MUNICIPIO']}</h6>
                    <p> Serología: </p>
                    <p>Positivas: {data.iloc[i]['POSITIVOS SEROLOGIA']}</p>
                    <p> Total: {data.iloc[i]['No DE PRUEBAS SEROLOGIA']}</p>
                    """
            iframe = folium.IFrame(html=html,width=130, height=160)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Circle(
                location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
                popup=popup,
                radius=float(data.iloc[i]['No DE PRUEBAS SEROLOGIA'])*100,
                color='lightgray',
                fill=True,
                fill_color='gray'
            ).add_to(m)

        for i in range(0,len(data)):
            html = f"""
                    <head>
                        <link rel="stylesheet" href="https://codepen.io/chriddyp/pen/dZVMbK.css">
                    <head>
                    <h6> {data.iloc[i]['MUNICIPIO']}</h6>
                    <p> Serología: </p>
                    <p>Positivas: {data.iloc[i]['POSITIVOS SEROLOGIA']}</p>
                    <p> Total: {data.iloc[i]['No DE PRUEBAS SEROLOGIA']}</p>
                    """
            iframe = folium.IFrame(html=html,width=130, height=160)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Circle(
                location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
                popup=popup,
                radius=float(data.iloc[i]['POSITIVOS SEROLOGIA'])*100,
                color='cadetblue',
                fill=True,
                fill_color='blue'
            ).add_to(m)

        # folium_hmap.save('assets/prueba_por_municipios.html')
    else:
        for i in range(0,len(data)):
            html = f"""
                    <head>
                        <link rel="stylesheet" href="https://codepen.io/chriddyp/pen/dZVMbK.css">
                    <head>
                    <h6> {data.iloc[i]['MUNICIPIO']}</h6>
                    <p> PCR: </p>
                    <p>Positivas: {data.iloc[i]['POSITIVOS PCR']}</p>
                    <p> Total: {data.iloc[i]['No DE PRUEBAS PCR']}</p>
                    """
            iframe = folium.IFrame(html=html,width=130, height=160)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Circle(
                location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
                popup=popup,
                radius=float(data.iloc[i]['No DE PRUEBAS PCR'])*100,
                color='lightgray',
                fill=True,
                fill_color='lightgray'
            ).add_to(m)
        for i in range(0,len(data)): #redundante
            html = f"""
                    <head>
                        <link rel="stylesheet" href="https://codepen.io/chriddyp/pen/dZVMbK.css">
                    <head>
                    <h6> {data.iloc[i]['MUNICIPIO']}</h6>
                    <p> PCR: </p>
                    <p>Positivas: {data.iloc[i]['POSITIVOS PCR']}</p>
                    <p> Total: {data.iloc[i]['No DE PRUEBAS PCR']}</p>
                    """
            iframe = folium.IFrame(html=html,width=130, height=160)
            popup = folium.Popup(iframe, max_width=2650)
            folium.Circle(
                location=[data.iloc[i]['lat'], data.iloc[i]['lon']],
                popup=popup,
                radius=float(data.iloc[i]['POSITIVOS PCR'])*100,
                color='crimson',
                fill=True,
                fill_color='crimson'
            ).add_to(m)
    folium_hmap.save('assets/prueba_por_municipios.html')

    return folium_hmap

#####################################################
# Importar los datos
#####################################################

df_ser = pd.read_csv('data/BDcomunitarioSeroprevalencia.csv')
df_pcr = pd.read_csv('data/pat_df2021GATEWAY.csv')
df_mur = pd.read_csv('data/BasedeDatosMurcielagosCórdoba_Dic2020.csv')

df_ser = pre_processing(df_ser,'sero')
df_pcr = pre_processing(df_pcr,'pcr')
df_mur = pre_processing(df_mur,'mur')

#####################################################
# layout callbacks 
#####################################################

@app.callback(
    Output('app-2-display-value', 'children'),
    Input('app-2-dropdown', 'value'))
def display_value2(value):
    return 'You have selected "{}"'.format(value)

#Grafico apilado
@app.callback(
    Output('bar_chart','figure'),
    [Input('barras_edad','value')]
)
def generate_bar(barras_edad):
    if barras_edad=='PCR':
        fig1 = apilado(df_pcr,'RESULTADO PCR','EDAD')
    else:
        fig1 = apilado(df_ser,'RESULTADO SEROLOGIA','EDAD')

    return fig1
#Grafico radial
@app.callback(
    Output('radial_plot','figure'),
    [Input('prueba_radial','value')]
)
def generate_radial(prueba_radial):
    if prueba_radial=='PCR':
        fig2 = radial_plot(df_pcr,'pcr')
    else:
        fig2 = radial_plot(df_ser,'sero')

    return fig2

#Actividad para actualizar gráficos dependiendo de la opción
@app.callback(
    Output('map','srcDoc'),
    [Input('prueba','value')]
)
def generate_map(prueba):
    if prueba=='Serologia':
        mapping_df(mun_to_coord(df_ser),prueba)
    else:
        mapping_df(mun_to_coord(df_pcr),prueba)
    return open('assets/prueba_por_municipios.html','r').read()

#Donut chart:
@app.callback(
    Output('donut_chart','figure'),
    [Input('variables','value')]
)
def generate_donut(variables):
    fig3 = donut_plot(df_mur,str(variables))
    return fig3

