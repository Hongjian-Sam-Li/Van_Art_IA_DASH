import pandas as pd
import dash_bootstrap_components as dbc
import dash
from dash import html, dcc, dash_table
import plotly.express as px
from dash.dependencies import Input, Output

# Read the CSV file and parse dates
public_art_data = pd.read_csv('../data/public-art.csv', sep=';', parse_dates=['YearOfInstallation'])

# Filter out rows with missing Neighbourhood values
public_art_data = public_art_data.dropna(subset=['Neighbourhood'])

# Get a sorted list of unique neighbourhoods
Types = sorted(public_art_data['Type'].unique())

# Extract the year from the 'YearOfInstallation' column
public_art_data['Year Of Installation'] = public_art_data['YearOfInstallation'].dt.year

# Define the column structure
pa_columns = [
    {'name': 'Title of Work', 'id': 'Title of Work'},
    {'name': 'Type', 'id': 'Type'},
    {'name': 'Year', 'id': 'Year Of Installation'},
    {'name': 'Location', 'id': 'SiteAddress'},
    {'name': 'Neighborhood', 'id': 'Neighbourhood'}
]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    
    dbc.Row([
        dbc.Col([
            html.H1("Van Art Dashboard")
        ])
    ]),
    dbc.Row([
            html.P('Explore the Public Arts in Vancouver!'),
        ]),
    dbc.Row([
        dbc.Col([
            html.H4("Select Art Type(s)"),
            dcc.Dropdown(
                
                id='type-dropdown',
                value=Types,
                options=[{'label': t, 'value': t} for t in Types],
                multi=True
            ),
        ]),
        dbc.Col([
            html.H4("Select Year Range"),
            dcc.RangeSlider(
                id='year-slider',
                min=1950,
                max=2022,
                step=1,
                value=[1950, 2022],
                marks={i: str(i) for i in range(1950, 2023, 10)}
            ),
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            html.H4("Public Art by Neighborhood", style={'marginBottom': '0.1rem'}),
            dcc.Graph(id='bar-plot')
        ]),
        dbc.Col([
            html.H4("Art Information"),
            dash_table.DataTable(
                id='art-table',
                columns=pa_columns,
                style_table={'overflowX': 'auto'},
                style_cell={'textAlign': 'left', 'width': '20%', 'minWidth': '100px', 'maxWidth': '300px'},
            ),
        ]),
    ]),
])

@app.callback(
    Output('bar-plot', 'figure'),
    Output('art-table', 'data'),
    Input('type-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_dashboard(selected_types, year_range):
    filtered_data = public_art_data[
        (public_art_data['Type'].isin(selected_types)) &
        (public_art_data['Year Of Installation'] >= year_range[0]) &
        (public_art_data['Year Of Installation'] <= year_range[1])
    ]
    neighborhood_counts = filtered_data.groupby('Neighbourhood').size().reset_index(name='count')
    bar_plot = px.bar(
        neighborhood_counts,
        x='Neighbourhood',
        y='count',
        labels={'count': 'Number of Arts'}
    )
    table_data = filtered_data[[col['id'] for col in pa_columns]].to_dict('records')
    return bar_plot, table_data

if __name__ == '__main__':
    app.run_server(debug=True)
