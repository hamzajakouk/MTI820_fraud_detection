#!/usr/bin/env python3
"""
Banking Transaction Dashboard
This script creates a simple dashboard to visualize banking transaction data from PostgreSQL.
"""

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

# PostgreSQL configuration
PG_HOST = 'localhost'
PG_PORT = 5432
PG_DATABASE = 'banking'
PG_USER = 'postgres'
PG_PASSWORD = 'postgres'  # Change this to your actual password

# Create the connection
def get_db_connection():
    """Get a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DATABASE,
        user=PG_USER,
        password=PG_PASSWORD
    )

# Query functions
def get_transaction_summary():
    """Get summary statistics of transactions."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_count,
                    SUM(CASE WHEN fraud_bool = 1 THEN 1 ELSE 0 END) as fraud_count,
                    AVG(income) as avg_income,
                    AVG(intended_balcon_amount) as avg_transaction_amount,
                    AVG(credit_risk_score) as avg_credit_score,
                    MIN(stream_timestamp) as first_transaction,
                    MAX(stream_timestamp) as last_transaction
                FROM banking_transactions
            """)
            result = cursor.fetchone()
            return result
    finally:
        conn.close()

def get_fraud_by_risk_category():
    """Get fraud distribution by risk category."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    risk_category,
                    SUM(CASE WHEN fraud_bool = 1 THEN 1 ELSE 0 END) as fraud_count,
                    COUNT(*) as total_count
                FROM banking_transactions
                GROUP BY risk_category
                ORDER BY risk_category
            """)
            results = cursor.fetchall()
            return pd.DataFrame(results)
    finally:
        conn.close()

def get_transactions_by_age_group():
    """Get transaction distribution by age group."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN customer_age < 25 THEN '18-24'
                        WHEN customer_age < 35 THEN '25-34'
                        WHEN customer_age < 45 THEN '35-44'
                        WHEN customer_age < 55 THEN '45-54'
                        WHEN customer_age < 65 THEN '55-64'
                        ELSE '65+'
                    END as age_group,
                    COUNT(*) as transaction_count,
                    SUM(CASE WHEN fraud_bool = 1 THEN 1 ELSE 0 END) as fraud_count,
                    AVG(intended_balcon_amount) as avg_amount
                FROM banking_transactions
                GROUP BY age_group
                ORDER BY age_group
            """)
            results = cursor.fetchall()
            return pd.DataFrame(results)
    finally:
        conn.close()

def get_transactions_by_payment_type():
    """Get transaction distribution by payment type."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    payment_type,
                    COUNT(*) as transaction_count,
                    SUM(CASE WHEN fraud_bool = 1 THEN 1 ELSE 0 END) as fraud_count
                FROM banking_transactions
                GROUP BY payment_type
                ORDER BY transaction_count DESC
            """)
            results = cursor.fetchall()
            return pd.DataFrame(results)
    finally:
        conn.close()

def get_latest_transactions(limit=10):
    """Get the latest transactions."""
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute("""
                SELECT 
                    id,
                    fraud_bool,
                    customer_age,
                    intended_balcon_amount,
                    payment_type,
                    employment_status,
                    credit_risk_score,
                    risk_category,
                    fraud_probability,
                    stream_timestamp
                FROM banking_transactions
                ORDER BY stream_timestamp DESC
                LIMIT %s
            """, (limit,))
            results = cursor.fetchall()
            return pd.DataFrame(results)
    finally:
        conn.close()

# Initialize the Dash app
app = dash.Dash(__name__, title="Banking Transaction Dashboard")

# App layout
app.layout = html.Div([
    html.H1("Banking Transaction Fraud Dashboard", style={'textAlign': 'center'}),
    
    html.Div([
        html.Button('Refresh Data', id='refresh-button', n_clicks=0),
        html.Div(id='last-update-time')
    ], style={'textAlign': 'right', 'marginBottom': '20px'}),
    
    # Summary cards
    html.Div([
        html.Div([
            html.H3("Total Transactions"),
            html.H2(id='total-transactions')
        ], className='summary-card'),
        html.Div([
            html.H3("Fraud Transactions"),
            html.H2(id='fraud-transactions')
        ], className='summary-card'),
        html.Div([
            html.H3("Fraud Rate"),
            html.H2(id='fraud-rate')
        ], className='summary-card'),
        html.Div([
            html.H3("Avg Transaction Amount"),
            html.H2(id='avg-amount')
        ], className='summary-card'),
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
    
    # Charts section
    html.Div([
        # Left column
        html.Div([
            html.H3("Fraud by Risk Category"),
            dcc.Graph(id='risk-category-chart')
        ], style={'width': '48%'}),
        
        # Right column
        html.Div([
            html.H3("Transactions by Age Group"),
            dcc.Graph(id='age-group-chart')
        ], style={'width': '48%'})
    ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
    
    html.Div([
        html.H3("Transactions by Payment Type"),
        dcc.Graph(id='payment-type-chart')
    ], style={'marginBottom': '20px'}),
    
    # Latest transactions table
    html.Div([
        html.H3("Latest Transactions"),
        dash_table.DataTable(
            id='transactions-table',
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'whiteSpace': 'normal',
                'height': 'auto',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{fraud_bool} = 1'},
                    'backgroundColor': 'rgba(255, 100, 100, 0.2)',
                    'color': 'red'
                }
            ]
        )
    ]),
    
    # Automatic refresh interval
    dcc.Interval(
        id='interval-component',
        interval=30*1000,  # 30 seconds in milliseconds
        n_intervals=0
    )
])

# Callbacks
@app.callback(
    [Output('total-transactions', 'children'),
     Output('fraud-transactions', 'children'),
     Output('fraud-rate', 'children'),
     Output('avg-amount', 'children'),
     Output('last-update-time', 'children'),
     Output('risk-category-chart', 'figure'),
     Output('age-group-chart', 'figure'),
     Output('payment-type-chart', 'figure'),
     Output('transactions-table', 'data'),
     Output('transactions-table', 'columns')],
    [Input('refresh-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')]
)
def update_dashboard(n_clicks, n_intervals):
    # Get summary data
    summary = get_transaction_summary()
    total_count = summary['total_count'] if summary else 0
    fraud_count = summary['fraud_count'] if summary else 0
    fraud_rate = f"{(fraud_count / total_count * 100):.2f}%" if total_count > 0 else "0.00%"
    avg_amount = f"${summary['avg_transaction_amount']:.2f}" if summary and summary['avg_transaction_amount'] else "$0.00"
    
    # Get chart data
    risk_data = get_fraud_by_risk_category()
    age_data = get_transactions_by_age_group()
    payment_data = get_transactions_by_payment_type()
    latest_data = get_latest_transactions()
    
    # Create figures
    if not risk_data.empty:
        risk_data['fraud_rate'] = risk_data['fraud_count'] / risk_data['total_count'] * 100
        risk_fig = px.bar(
            risk_data, 
            x="risk_category", 
            y=["fraud_count", "total_count"], 
            barmode="group",
            labels={"value": "Count", "variable": "Type"},
            title="Fraud by Risk Category"
        )
    else:
        risk_fig = go.Figure()
    
    if not age_data.empty:
        age_fig = px.bar(
            age_data, 
            x="age_group", 
            y="transaction_count",
            color="fraud_count",
            labels={"transaction_count": "Transactions", "age_group": "Age Group"},
            text="fraud_count",
            title="Transactions by Age Group"
        )
    else:
        age_fig = go.Figure()
    
    if not payment_data.empty:
        payment_fig = px.pie(
            payment_data, 
            values="transaction_count", 
            names="payment_type",
            title="Transactions by Payment Type"
        )
    else:
        payment_fig = go.Figure()
    
    # Format table data
    if not latest_data.empty:
        # Convert timestamps
        latest_data['stream_timestamp'] = pd.to_datetime(latest_data['stream_timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
        # Format amounts
        latest_data['intended_balcon_amount'] = latest_data['intended_balcon_amount'].apply(lambda x: f"${x:.2f}")
        # Format fraud boolean
        latest_data['fraud_bool'] = latest_data['fraud_bool'].apply(lambda x: "Yes" if x == 1 else "No")
        # Format fraud probability as percentage
        latest_data['fraud_probability'] = latest_data['fraud_probability'].apply(lambda x: f"{x*100:.2f}%")
        
        table_data = latest_data.to_dict('records')
        table_columns = [{"name": col.replace('_', ' ').title(), "id": col} for col in latest_data.columns]
    else:
        table_data = []
        table_columns = []
    
    # Current time for update display
    update_time = f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return (
        f"{total_count:,}",
        f"{fraud_count:,}",
        fraud_rate,
        avg_amount,
        update_time,
        risk_fig,
        age_fig,
        payment_fig,
        table_data,
        table_columns
    )

# Add CSS styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .summary-card {
                background-color: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                width: 22%;
                text-align: center;
            }
            .summary-card h3 {
                margin-top: 0;
                color: #666;
                font-size: 16px;
            }
            .summary-card h2 {
                margin-bottom: 0;
                font-size: 28px;
                color: #1E88E5;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
