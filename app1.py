import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_echarts import DashECharts
import dash_table
import datetime

app = dash.Dash(__name__)

missiles_daily = pd.read_csv('/Users/ayasiratalan/Desktop/ACADEMIA/Ukraine_Russia/Russian_Missile_Attacks/deploy_python_Feb_7/missiles_daily.csv', parse_dates=['Date'])
dat_expanded_preprocessed = pd.read_csv('/Users/ayasiratalan/Desktop/ACADEMIA/Ukraine_Russia/Russian_Missile_Attacks/deploy_python_Feb_7/dat_expanded_preprocessed.csv', parse_dates=['Date'])

missiles_daily['Date'] = pd.to_datetime(missiles_daily['Date'])
dat_expanded_preprocessed['Date'] = pd.to_datetime(dat_expanded_preprocessed['Date'])

def create_date_marks(dates, num_marks=4):
    min_date = dates.min()
    max_date = dates.max()
    date_range = pd.date_range(start=min_date, end=max_date, periods=num_marks)
    date_marks = {
        int(pd.Timestamp(date).timestamp() * 1000): date.strftime('%Y-%m-%d')
        for date in date_range
    }
    return date_marks

date_marks = create_date_marks(missiles_daily['Date'], num_marks=4)

app.layout = html.Div([

    html.Div([

        html.Div([
            DashECharts(
                option={},  
                id='missile-plot',
                style={'width': '100%', 'height': '500px'}
            ),
        ], style={'border': '1px solid #ccc', 'padding': '10px', 'marginBottom': '20px'}),

        html.Div([
            dcc.RangeSlider(
                id='date-range-slider',
                min=int(missiles_daily['Date'].min().timestamp() * 1000),
                max=int(missiles_daily['Date'].max().timestamp() * 1000),
                value=[
                    int(missiles_daily['Date'].min().timestamp() * 1000),
                    int(missiles_daily['Date'].max().timestamp() * 1000)
                ],
                marks=date_marks,
                step=None,
                tooltip={'always_visible': False, 'placement': 'bottom'}
            ),
        ], style={'marginBottom': '20px'}),

        # Center the 'Model Details' title
        html.H2("Model Details", style={'fontFamily': 'Optima, sans-serif', 'textAlign': 'center'}),

        html.Div(id='table-container', style={'display': 'none', 'border': '1px solid #ccc', 'padding': '10px'}),

        # Updated 'Using This Dashboard' section
        html.Div([
            html.H3("Using This Dashboard", style={
                'fontFamily': 'Optima, sans-serif',
                'textAlign': 'center',
                'marginTop': '40px'
            }),
            html.Div([
                html.P(
                    "This interactive dashboard explores the daily and cumulative trends of Russian missile attacks, including the number of missiles (UAVs included) launched, types of missiles used, and the success of Ukrainian intercepts. Use the date range slider below the chart to select a specific time period. The chart will update to display the number of missiles launched and destroyed during the selected date range. Hover over the bars in the chart to view detailed information for each date. In the 'Model Details' section below, a table provides additional data on the missile attacks. You can search for a specific date using the search box in the 'Date' column. Note: The term 'destroyed' includes missiles that were intercepted plus that went missing due to electronic warfare tools.",
                    style={
                        'textAlign': 'justify',
                        'margin': '0 auto',
                        'padding': '10px',
                        'fontFamily': 'Optima, sans-serif'
                    }
                ),
            ], style={
                'border': '1px solid #ccc',
                'padding': '10px',
                'maxWidth': '800px',
                'margin': '0 auto'
            }),
        ], style={'padding': '10px', 'maxWidth': '1200px', 'margin': '0 auto'})

    ])

])

def create_echarts_option(filtered_df):
    option = {
        'useUTC': True, 
        'title': {
            'text': 'Daily Tally of Russian Missile Attacks',
            'left': 'center',
            'textStyle': {
                'fontFamily': 'Optima, sans-serif'
            }
        },
        'tooltip': {'trigger': 'axis'},
        'legend': {
            'data': ['Launched', 'Destroyed'],
            'bottom': 0,
            'textStyle': {
                'fontFamily': 'Optima, sans-serif'
            }
        },
        'grid': {
            'left': '10%',
            'right': '10%',
            'bottom': '20%',
            'containLabel': True
        },
        'xAxis': {
            'type': 'time',
            'name': 'Date',
            'nameTextStyle': {
                'fontFamily': 'Optima, sans-serif'
            },
            'axisLabel': {
                'formatter': '{yyyy}-{MM}-{dd}',
                'fontFamily': 'Optima, sans-serif',
                'rotate': 45,
                'hideOverlap': True,
                'interval': 'auto'
            },
            'axisTick': {
                'alignWithLabel': True
            },
            'splitLine': {
                'show': False
            },
            'minorTick': {
                'show': False
            },
            'minorSplitLine': {
                'show': False
            }
        },
        'yAxis': {
            'type': 'value',
            'name': 'Count',
            'nameTextStyle': {
                'fontFamily': 'Optima, sans-serif'
            },
            'axisLabel': {
                'fontFamily': 'Optima, sans-serif'
            }
        },
        'dataZoom': [
            {
                'type': 'slider',
                'show': True,
                'xAxisIndex': 0,
                'orient': 'horizontal',
                'height': 20
            }
        ],
        'series': [
            {
                'name': 'Launched',
                'type': 'bar',
                'data': filtered_df.apply(
                    lambda x: [int(x['Date'].timestamp() * 1000), x['total_launched']], axis=1).tolist(),
                'itemStyle': {'color': '#0fb7ca'},
                'showSymbol': False,
                'connectNulls': False
            },
            {
                'name': 'Destroyed',
                'type': 'bar',
                'data': filtered_df.apply(
                    lambda x: [int(x['Date'].timestamp() * 1000), x['total_destroyed']], axis=1).tolist(),
                'itemStyle': {'color': '#2b0b83', 'opacity': 0.7},
                'showSymbol': False,
                'connectNulls': False
            }
        ],
        'markLine': {'data': []},
        'markPoint': {'data': []}
    }
    return option

@app.callback(
    Output('missile-plot', 'option'),
    Input('date-range-slider', 'value')
)
def update_graph(date_range):
    start_date = pd.to_datetime(date_range[0], unit='ms')
    end_date = pd.to_datetime(date_range[1], unit='ms')

    filtered_df = missiles_daily[
        (missiles_daily['Date'] >= start_date) &
        (missiles_daily['Date'] <= end_date)
    ]

    option = create_echarts_option(filtered_df)
    return option

@app.callback(
    Output('table-container', 'children'),
    Output('table-container', 'style'),
    Input('date-range-slider', 'value')
)
def update_table(date_range):
    start_date = pd.to_datetime(date_range[0], unit='ms')
    end_date = pd.to_datetime(date_range[1], unit='ms')

    filtered_data = dat_expanded_preprocessed[
        (dat_expanded_preprocessed['Date'] >= start_date) &
        (dat_expanded_preprocessed['Date'] <= end_date)
    ]
    if filtered_data.empty:
        return html.Div("No data available for the selected date range."), {'display': 'none'}
    else:
        filtered_data['Date'] = filtered_data['Date'].dt.strftime('%Y-%m-%d')

        # Define columns with placeholder text only for the 'Date' column
        columns = []
        for i in filtered_data.columns:
            if i == 'Date':
                columns.append({
                    'name': i,
                    'id': i,
                    'filter_options': {'placeholder_text': 'Search for a specific date'}
                })
            else:
                columns.append({'name': i, 'id': i})

        table = dash_table.DataTable(
            data=filtered_data.to_dict('records'),
            columns=columns,
            page_size=10,
            filter_action='native',
            sort_action='native',
            style_table={
                'overflowX': 'auto',
                'border': '1px solid #ccc',
                'borderRadius': '5px',
            },
            style_cell={
                'textAlign': 'left',
                'padding': '5px',
                'backgroundColor': '#f9f9f9',
                'fontFamily': 'Optima, sans-serif',
            },
            style_header={
                'backgroundColor': '#4c3d75',
                'fontWeight': 'bold',
                'color': 'white',
                'fontFamily': 'Optima, sans-serif',
            },
            style_data={
                'whiteSpace': 'normal',
                'height': 'auto',
                'fontFamily': 'Optima, sans-serif',
            },
            # Style the filter boxes to make them more obvious
            style_filter={
                'backgroundColor': '#e6e6e6',
                'fontFamily': 'Optima, sans-serif',
                'color': '#333',
                'border': '1px solid #ccc',
            }
        )

        return table, {'display': 'block', 'border': '1px solid #ccc', 'padding': '10px'}

if __name__ == '__main__':
    app.run_server(debug=False)
