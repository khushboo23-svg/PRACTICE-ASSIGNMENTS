import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# ── Load data ──────────────────────────────────────────────────────────────────
data = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/d51iMGfp_t0QpO30Lym-dw/automobile-sales.csv')

# ── App init ───────────────────────────────────────────────────────────────────
app = dash.Dash(__name__)

app.title = "Automobile Statistics Dashboard"

# ── Dropdown options ───────────────────────────────────────────────────────────
dropdown_options = [
    {'label': 'Yearly Statistics',            'value': 'Yearly Statistics'},
    {'label': 'Recession Period Statistics',  'value': 'Recession Period Statistics'},
]

year_list = [i for i in range(1980, 2024, 1)]

# ── Layout ─────────────────────────────────────────────────────────────────────
app.layout = html.Div([

    # TASK 2.1 – Dashboard title
    html.H1(
        "Automobile Sales Statistics Dashboard",
        style={'color': '#503D36', 'fontSize': 24, 'textAlign': 'center'}
    ),

    # TASK 2.2 – Dropdown 1: Report type
    html.Div([
        html.Label("Select Statistics:"),
        dcc.Dropdown(
            id='dropdown-statistics',
            options=dropdown_options,
            value='Yearly Statistics',          # default selection
            placeholder='Select a report type'
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

    # Dropdown 2: Year (enabled only for Yearly Statistics)
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='select-year',
            options=[{'label': i, 'value': i} for i in year_list],
            value=2020,                          # default year
            placeholder='Select a year'
        )
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

    # TASK 2.3 – Output container (2 rows × 2 cols)
    html.Div([
        html.Div(id='output-container', className='chart-item',
                 style={'display': 'flex', 'flexWrap': 'wrap'})
    ])
])


# ── TASK 2.4 – Callback 1: enable / disable year dropdown ─────────────────────
@app.callback(
    Output(component_id='select-year',       component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    # Year dropdown is ACTIVE only when 'Yearly Statistics' is chosen
    if selected_statistics == 'Yearly Statistics':
        return False   # not disabled → user can pick a year
    else:
        return True    # disabled → year is irrelevant for recession view


# ── Callback 2: render the four charts ────────────────────────────────────────
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year',         component_property='value')]
)
def update_output_container(selected_statistics, input_year):

    # ═══════════════════════════════════════════════════════════════════════════
    # TASK 2.5 – RECESSION PERIOD STATISTICS
    # ═══════════════════════════════════════════════════════════════════════════
    if selected_statistics == 'Recession Period Statistics':

        recession_data = data[data['Recession'] == 1]

        # Plot 1 – Line: average automobile sales per year during recessions
        yearly_rec = (recession_data
                      .groupby('Year')['Automobile_Sales']
                      .mean()
                      .reset_index())

        R_chart1 = dcc.Graph(
            figure=px.line(
                yearly_rec,
                x='Year',
                y='Automobile_Sales',
                title='Average Automobile Sales Fluctuation over Recession Period'
            )
        )

        # Plot 2 – Bar: average sales by vehicle type during recessions
        average_sales = (recession_data
                         .groupby('Vehicle_Type')['Automobile_Sales']
                         .mean()
                         .reset_index())

        R_chart2 = dcc.Graph(
            figure=px.bar(
                average_sales,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title='Average Vehicles Sold by Vehicle Type during Recession'
            )
        )

        # Plot 3 – Pie: total advertising expenditure share by vehicle type
        exp_rec = (recession_data
                   .groupby('Vehicle_Type')['Advertising_Expenditure']
                   .sum()
                   .reset_index())

        R_chart3 = dcc.Graph(
            figure=px.pie(
                exp_rec,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title='Total Advertising Expenditure Share by Vehicle Type during Recession'
            )
        )

        # Plot 4 – Bar: unemployment rate effect on vehicle type & sales
        unemp_data = (recession_data
                      .groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales']
                      .mean()
                      .reset_index())

        R_chart4 = dcc.Graph(
            figure=px.bar(
                unemp_data,
                x='unemployment_rate',
                y='Automobile_Sales',
                color='Vehicle_Type',
                labels={
                    'unemployment_rate': 'Unemployment Rate',
                    'Automobile_Sales':  'Average Automobile Sales'
                },
                title='Effect of Unemployment Rate on Vehicle Type and Sales'
            )
        )

        # Return: 2 rows × 2 cols layout
        return [
            html.Div(
                className='chart-item',
                children=[R_chart1, R_chart2],
                style={'display': 'flex', 'flex': '1 1 100%'}
            ),
            html.Div(
                className='chart-item',
                children=[R_chart3, R_chart4],
                style={'display': 'flex', 'flex': '1 1 100%'}
            )
        ]

    # ═══════════════════════════════════════════════════════════════════════════
    # TASK 2.6 – YEARLY STATISTICS
    # ═══════════════════════════════════════════════════════════════════════════
    elif input_year and selected_statistics == 'Yearly Statistics':

        yearly_data = data[data['Year'] == input_year]

        # Plot 1 – Line: whole-period yearly average automobile sales
        yas = (data
               .groupby('Year')['Automobile_Sales']
               .mean()
               .reset_index())

        Y_chart1 = dcc.Graph(
            figure=px.line(
                yas,
                x='Year',
                y='Automobile_Sales',
                title='Yearly Average Automobile Sales (all years)'
            )
        )

        # Plot 2 – Line: total monthly automobile sales for selected year
        mas = (yearly_data
               .groupby('Month')['Automobile_Sales']
               .sum()
               .reset_index())

        Y_chart2 = dcc.Graph(
            figure=px.line(
                mas,
                x='Month',
                y='Automobile_Sales',
                title=f'Total Monthly Automobile Sales in {input_year}'
            )
        )

        # Plot 3 – Bar: average vehicles sold by vehicle type in selected year
        avr_vdata = (yearly_data
                     .groupby('Vehicle_Type')['Automobile_Sales']
                     .mean()
                     .reset_index())

        Y_chart3 = dcc.Graph(
            figure=px.bar(
                avr_vdata,
                x='Vehicle_Type',
                y='Automobile_Sales',
                title=f'Average Vehicles Sold by Vehicle Type in {input_year}'
            )
        )

        # Plot 4 – Pie: total advertising expenditure by vehicle type in selected year
        exp_data = (yearly_data
                    .groupby('Vehicle_Type')['Advertising_Expenditure']
                    .sum()
                    .reset_index())

        Y_chart4 = dcc.Graph(
            figure=px.pie(
                exp_data,
                values='Advertising_Expenditure',
                names='Vehicle_Type',
                title=f'Total Advertising Expenditure by Vehicle Type in {input_year}'
            )
        )

        # Return: 2 rows × 2 cols layout
        return [
            html.Div(
                className='chart-item',
                children=[Y_chart1, Y_chart2],
                style={'display': 'flex', 'flex': '1 1 100%'}
            ),
            html.Div(
                className='chart-item',
                children=[Y_chart3, Y_chart4],
                style={'display': 'flex', 'flex': '1 1 100%'}
            )
        ]

    else:
        return None


# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)