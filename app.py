import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output, State
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# https://htmlcheatsheet.com/css/

######################################################Data##############################################################


df = pd.read_excel('Flight_Dataset_last_version.xlsx')

type_names = ['Departure', 'Arrival']

unit_names = ['Flights', 'Passengers']

######################################################Interactive Components############################################

country_options = [dict(label=country, value=country) for country in df['Country'].unique()] + \
                  [{'label': 'All', 'value': 'All Countries'}]

type_options = [dict(label=type.replace('_', ' '), value=type) for type in type_names]

unit_options = [dict(label=unit.replace('_', ' '), value=unit) for unit in unit_names]


dropdown_country = dcc.Dropdown(
        id='country_drop',
        options=country_options,
        value='All Countries'
    )


Radio_type = dcc.RadioItems(
    id='type_option',
    options=type_options,
    value='Arrival'
)

Radio_unit = dcc.RadioItems(
        id='unit_option',
        options=unit_options,
        value='Flights'
    )

slider_year = dcc.RangeSlider(
        id='year_slider',
        min=2010,
        max=2020,
        marks={i: '{}'.format(i) for i in
               [2010, 2011, 2012,2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
               },
        value=[2010,2020],
        step=1
    )



##################################################APP###################################################################

app = dash.Dash(__name__)

server = app.server

app.layout = html.Div([

    html.Div([
        html.H1('Flight and passenger movements in the Europe'),
    ], id='1st row', className='pretty_box'),
    html.Div([
        html.Div([
            html.Div([
                html.Label('Countries'),
                dropdown_country,
                html.Br(),
                html.Label('Type Choice'),
                Radio_type,
                html.Br(),
                html.Label('Unit Choice'),
                Radio_unit,
                html.Br(),
                html.Label('Year Slider'),
                slider_year]),
            html.Div([
                html.Img(src=app.get_asset_url('10001.png'),style={'margin': '3%'}),
                html.Br(),
                dcc.Markdown("""\
                  - Gabriel Felipe Martins de Souza, m20210598.   
                  - Luiz Humberto Polaro Vizeu, m20210554.
                  - Rogério Domingos Paulo, m20210597.  
                """, style={"text-align": "center", "font-size": "10pt",'justify':"center",'padding-top': '10%',
                            'padding-bottom': '5%','align':"center",'vertical-align':'middle'}),
            ], style={'display': 'flex'})
        ], id='Iteraction', style={'width': '30%'}, className='pretty_box'),
        html.Div([
                dcc.Graph(id='Map'),
            ], id='MAP', style={'width': '40%'}, className='pretty_box'),
        html.Div([
            dcc.Graph(id='Barline'),
        ], id='BARLINE', style={'width': '30%'}, className='pretty_box'),
    ], id='2nd row', style={'display': 'flex'}),
    html.Div([
        html.Div([
            dcc.Graph(id='Treemap'),
        ], id='TREEMAP', style={'width': '70%'}, className='pretty_box'),
        html.Div([
            dcc.Graph(id='Lines'),
        ], id='LINES', style={'width': '30%'}, className='pretty_box')
    ], id='3rd row', style={'display': 'flex'})
])


######################################################1Callbacks#########################################################


@app.callback(

        Output("Map", "figure")
    ,
    [
        Input("year_slider", "value"),
        Input("country_drop", "value"),
        Input("type_option", "value"),
        Input('unit_option', 'value')
    ]
)
def plots(years, countries,type,unit):
    ############################################First Map Plot##########################################################
    if countries == 'All Countries':
        dff = df
    else:
        dff = df[df.Country.isin([countries])]

    year_selected = (dff['Year'] >= years[0]) & (dff['Year'] <= years[1])
    data_map = dff[year_selected]
    data_map = data_map[data_map['Type'] == type]
    data_map = data_map[data_map['Unit'] == unit]

    if unit == 'Flights':
        scale = 20000
    else:
        scale = 2000000

    fig = go.Figure(go.Scattergeo(locations=data_map.Country, locationmode='country names', marker=dict(
        size=data_map['Value']/scale,color=['mistyrose','steelblue','lemonchiffon','lightsteelblue','wheat',
                                            'ivory','cornsilk','limegreen','palegoldenrod','mediumaquamarine',
                                            'slategrey','rebeccapurple','beige','midnightblue','indigo','lavenderblush',
                                            'rosybrown','gray','lightgoldenrodyellow','dimgray','turquoise','olivedrab',
                                            'indianred','teal', 'lightslategrey','darksalmon','fuchsia','purple',
                                            'darkslategrey','snow','aqua']),text = data_map[['Year','Type','Unit','Value']] ))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180,
                      geo=dict(scope='europe',
                                      landcolor='white',
                                      lakecolor='white',
                                      bgcolor='#f9f9f9',
                                      ))
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0},paper_bgcolor='rgba(0,0,0,0)',
                             plot_bgcolor='rgba(0,0,0,0)')

    return fig

######################################################2Callbacks#########################################################


@app.callback(

        Output("Treemap", "figure")
    ,
    [
        Input("year_slider", "value"),
        Input("type_option", "value"),
        Input('unit_option', 'value')
    ]
)
def plots(years,type,unit):
    ############################################ TreeMap Plot##########################################################

    year_selected = (df['Year'] >= years[0]) & (df['Year'] <= years[1])

    df_treemap = df[year_selected]
    df_treemap = df_treemap[df_treemap.Type == type]
    df_treemap = df_treemap[df_treemap.Unit == unit]

    fig = px.treemap(df_treemap, path=[px.Constant("Europe"), 'Country'], values='Value',
                     color='Value', hover_data=['Country'],
                     color_continuous_scale='RdBu',
                     color_continuous_midpoint=np.average(df_treemap['Value'], weights=df_treemap['Value']))
    fig.update_layout(margin=dict(t=50, l=25, r=25, b=25),title=dict(text='Treemap'+' '+str(type)+' '
                                                                          +str(unit)+' in '+str(years)))
    fig.data[0].textinfo = 'label+text+value+percent entry+current path'

    return fig

######################################################3Callbacks#########################################################


@app.callback(

        Output("Barline", "figure")
    ,
    [
        Input("country_drop", "value"),
    ]
)
def plots(countries):
    ############################################ barline Plot##########################################################
    if countries == 'All Countries':
        df_barline = df
    else:
        df_barline = df[df.Country.isin([countries])]

    df_barline = pd.pivot_table(df_barline, values=['Value'], index=['Year', 'Unit'], aggfunc={'Value': sum}).reset_index()
    df_fl = df_barline[df_barline['Unit'] == 'Flights']
    df_ps = df_barline[df_barline['Unit'] == 'Passengers']

    ex_trace1 = dict(type='bar',
                     x=df_fl['Year'],
                     y=df_fl['Value'] ,
                     name='Flights'
                     )
    ex_trace2 = dict(type='scatter',
                     x=df_ps['Year'],
                     y=df_ps['Value']/1000,
                     name=' Passangers * K',
                     )
    ex_data = [ex_trace1, ex_trace2]

    ex_layout = dict(title=dict(text='From 2010 to 2020 Flights and Passengers'+' in '+str(countries)),
                     xaxis=dict(title='Passangers numbers calculated in thousands of people'),
                     yaxis=dict(title='Flights & Passengers')
                     )

    ex_fig = go.Figure(data=ex_data, layout=ex_layout)

    return ex_fig

######################################################4Callbacks#########################################################


@app.callback(

        Output("Lines", "figure")
    ,
    [
        Input("year_slider", "value"),
    ]
)
def plots(years):
    ############################################ Lines chart##########################################################

    year_selected = (df['Year'] >= years[0]) & (df['Year'] <= years[1])

    df_linechart = df[year_selected]
    df_linechart = pd.pivot_table(df_linechart, values=['Value'], index=['Country', 'Unit'], aggfunc={'Value': sum}).reset_index()
    df_fl = df_linechart[df_linechart['Unit'] == 'Flights']
    df_ps = df_linechart[df_linechart['Unit'] == 'Passengers']

    ex_trace3 = dict(type='scatter',
                     x=df_fl['Country'],
                     y=df_fl['Value'],
                     name='Flights'
                     )
    ex_trace4 = dict(type='scatter',
                     x=df_ps['Country'],
                     y=df_ps['Value'],
                     name=' Passangers * K'
                     )
    ex_data1 = [ex_trace3, ex_trace4]

    ex_layout1 = dict(title=dict(text='Passengers by Flight by Location'+' in '+str(years)),
                      xaxis=dict(title='Passangers numbers calculated in thousands of people'),
                      yaxis=dict(title='Flights & Passengers')
                      )

    ex_fig1 = go.Figure(data=ex_data1, layout=ex_layout1)

    return ex_fig1


if __name__ == '__main__':
    app.run_server(debug=True)
