import dash_core_components as dcc
import dash_html_components as html
import callbacks

#####################
# Nav bar
def get_navbar(p = 'gen'):

    navbar_gen = html.Div([

        html.Div([], className = 'three columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'General Overview'),
                href='/general_overview'),
        ],className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Pacientes'),
                href='/apps/pacientes'
                )
        ],
        className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Murcielagos'),
                href='/apps/murcielagos'
                )
        ],
        className='two columns'),

        html.Div([], className = 'three columns')

    ],
    className = 'row'
    )

    navbar_page2 = html.Div([

        html.Div([], className = 'three columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'General Overview'),
                href='/general_overview'
                )
        ],
        className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Pacientes'),
                href='/apps/pacientes'
                )
        ],
        className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Murcielagos'),
                href='/apps/murcielagos'
                )
        ],
        className='two columns'),

        html.Div([], className = 'three columns')

    ],
    className = 'row'
    )

    navbar_page3 = html.Div([

        html.Div([], className = 'three columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'General Overview'),
                href='/general_overview'
                )
        ],
        className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Pacientes'),
                href='/apps/pacientes'
                )
        ],
        className='two columns'),

        html.Div([
            dcc.Link(
                html.H6(children = 'Murcielagos'),
                href='/apps/murcielagos'
                )
        ],
        className='two columns'),

        html.Div([], className = 'three columns')

    ],
    className = 'row'
    )

    if p == 'gen':
        return navbar_gen
    elif p == 'page2':
        return navbar_page2
    else:
        return navbar_page3


layout0 = html.Div([
        get_navbar('gen'),
        html.Div([
            html.H1(children='ControlBox'),
            html.P('Sistema de información para la caracterización, identificación, información, y previsión de riesgo de contagio por covid-19.'),
            html.Div(children='''
                En este es el Dashboard puede encontrar
                toda la información relacionada al proyecto
                ControlBox
            '''),
           
        ], className='row'),
        html.Div([
            html.H3(children='Analisis de Edad'),

            html.P('Prueba:'),
            dcc.Dropdown(
                id='barras_edad',
                value='PCR',
                options=[{'value':x, 'label':x}
                        for x in ['PCR','Serologia']],
                clearable=False   
            ),
            dcc.Graph(
                id='bar_chart',
                config={
                'displayModeBar': False
            }
            ),  
        ], className='row')

])

layout1 = html.Div([
    get_navbar('page2'),
    html.Div([
        
        html.H3(children='Síntomas'),
        html.P('Prueba:'),
            dcc.Dropdown(
                id='prueba_radial',
                value='Serologia',
                options=[{'value':x, 'label':x}
                        for x in ['PCR','Serologia']],
                clearable=False   
            ),
        dcc.Graph(
            id='radial_plot',
            config={
            'displayModeBar': False
            })
    ],className='eight columns'),
        html.Div([
            html.H3(children='Mapa de Pruebas'),
            html.P('Prueba:'),
            dcc.Dropdown(
                id='prueba',
                value='Serologia',
                options=[{'value':x, 'label':x}
                        for x in ['PCR','Serologia']],
                clearable=False   
            ),
            html.Iframe(id='map',#graficamos el mapa como un Iframe
            srcDoc=open('static/prueba_por_municipios.html','r').read(),width='90%',height='400')
                ],className = 'four columns'),
        ], className = 'row')

layout2 = html.Div([
    get_navbar('page3'),
    html.H3(children='Murcielagos'),

            html.Div(children='''
                Murcielagos
            '''),
            html.P('Variable:'),
            dcc.Dropdown(
                id='variables',
                value='Lugar',
                options=[{'value':x, 'label':x}
                        for x in ['Fecha de  toma de muestra','Lugar','Urb/Rural','Especie','Sexo']], #df_mur.columns[2:8]]
                clearable=False   
            ),
            dcc.Graph(
                id='donut_chart',
                config={
                'displayModeBar': False
                }
                #figure=fig3
            ),  
        ], className='row')
