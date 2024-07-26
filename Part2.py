import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import requests
from io import StringIO

# Fetch and read the data from the URL
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-DV0101EN-SkillsNetwork/Data%20Files/historical_automobile_sales.csv"
response = requests.get(url)
data = response.content.decode('utf-8')
df = pd.read_csv(StringIO(data))

# Initialize the Dash app
app = Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={
            'textAlign': 'center',
            'color': '#503D36',
            'fontSize': '24px'
        }
    ),
    
    # Dropdown for selecting report type
    dcc.Dropdown(
        id='dropdown-statistics',
        options=[
            {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
            {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
        ],
        placeholder='Select a report type',
        value='Select Statistics',
        style={
            'width': '80%',
            'padding': '3px',
            'fontSize': '20px',
            'textAlignLast': 'center'
        }
    ),
    
    # Dropdown for selecting year
    dcc.Dropdown(
        id='select-year',
        options=[{'label': str(i), 'value': i} for i in range(1980, 2024)],
        placeholder='Select a year',
        value=None,  # Changed to None for proper behavior
        style={
            'width': '80%',
            'padding': '3px',
            'fontSize': '20px',
            'textAlignLast': 'center'
        }
    ),
    
    # Division for output display
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex', 'flexDirection': 'column'})
])

# Define the callback to enable/disable year dropdown
@app.callback(
    Output('select-year', 'disabled'),
    Input('dropdown-statistics', 'value')
)
def update_input_container(selected_statistics):
    return selected_statistics != 'Yearly Statistics'

# Define the callback to update the output container with plots
@app.callback(
    Output('output-container', 'children'),
    [Input('dropdown-statistics', 'value'),
     Input('select-year', 'value')]
)
def update_output_container(selected_statistics, selected_year):
    if selected_statistics == 'Recession Period Statistics':
        # Filter the data for recession periods
        recession_data = df[df['Recession'] == 1]
        
        # Plot 1: Automobile sales fluctuate over Recession Period (year-wise) using line chart
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(
            figure=px.line(yearly_rec, 
                x='Year',
                y='Automobile_Sales',
                title="Automobile Sales Fluctuations during Recession"
            )
        )
        
        # Plot 2: Average number of vehicles sold by vehicle type (Bar chart)
        average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
        R_chart2 = dcc.Graph(
            figure=px.bar(average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title="Average Number of Vehicles Sold by Vehicle Type during Recession"
            )
        )
        
        # Plot 3: Pie chart for total expenditure share by vehicle type during recessions
        exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
        R_chart3 = dcc.Graph(
            figure=px.pie(exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title="Total Advertisement Expenditure Share by Vehicle Type during Recession"
            )
        )
        
        # Plot 4: Bar chart for the effect of unemployment rate on vehicle type and sales
        unemp_data = recession_data.groupby(['Unemployment_Rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
        R_chart4 = dcc.Graph(
            figure=px.bar(unemp_data,
                x='Unemployment_Rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                labels={'Unemployment_Rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
                title='Effect of Unemployment Rate on Vehicle Type and Sales during Recession'
            )
        )
        
        return [
            html.Div(className='chart-item', children=[html.Div(children=R_chart1), html.Div(children=R_chart2)], style={'display': 'flex', 'flexDirection': 'row'}),
            html.Div(className='chart-item', children=[html.Div(children=R_chart3), html.Div(children=R_chart4)], style={'display': 'flex', 'flexDirection': 'row'})
        ]
    
    elif selected_statistics == 'Yearly Statistics':
        if selected_year:
            # Filter data based on the selected year
            yearly_data = df[df['Year'] == selected_year]
            
            # Plot 1: Yearly Automobile sales using line chart for the whole period
            yas = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
            Y_chart1 = dcc.Graph(
                figure=px.line(yas,
                    x='Year',
                    y='Automobile_Sales',
                    title='Yearly Automobile Sales'
                )
            )
            
            # Plot 2: Total Monthly Automobile sales using line chart
            mas = df.groupby('Month')['Automobile_Sales'].sum().reset_index()
            Y_chart2 = dcc.Graph(
                figure=px.line(mas,
                    x='Month',
                    y='Automobile_Sales',
                    title='Total Monthly Automobile Sales'
                )
            )
            
            # Plot 3: Average number of vehicles sold during the given year
            avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
            Y_chart3 = dcc.Graph(
                figure=px.bar(avr_vdata,
                    x='Vehicle_Type',
                    y='Automobile_Sales',
                    title=f'Average Vehicles Sold by Vehicle Type in the Year {selected_year}'
                )
            )
            
            # Plot 4: Total Advertisement Expenditure for each vehicle using pie chart
            exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
            Y_chart4 = dcc.Graph(
                figure=px.pie(exp_data,
                    values='Advertising_Expenditure',
                    names='Vehicle_Type',
                    title='Total Advertisement Expenditure for Each Vehicle'
                )
            )
            
            return [
                html.Div(className='chart-item', children=[html.Div(children=Y_chart1), html.Div(children=Y_chart2)], style={'display': 'flex', 'flexDirection': 'row'}),
                html.Div(className='chart-item', children=[html.Div(children=Y_chart3), html.Div(children=Y_chart4)], style={'display': 'flex', 'flexDirection': 'row'})
            ]
        else:
            return []

# Run the application
if __name__ == '__main__':
    app.run_server(debug=True)
