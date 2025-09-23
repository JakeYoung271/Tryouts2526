import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import json
import time
from datetime import datetime

# Initialize Dash app with Bootstrap theme for mobile responsiveness
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Spikeball Tournament"

# Google Sheets configuration (you'll need to set up your credentials)
# Replace with your actual Google Sheets setup
SCOPES = ['https://www.googleapis.com/spreadsheets/readonly', 
          'https://www.googleapis.com/spreadsheets/']

# You'll need to add your service account credentials here
# For demo purposes, we'll use placeholder functions
def get_google_sheets_client():
    """Initialize Google Sheets client - replace with actual credentials"""
    # creds = Credentials.from_service_account_file('path/to/credentials.json', scopes=SCOPES)
    # return gspread.authorize(creds)
    return None

def check_user_exists(email):
    """Check if user exists in Google Sheets and return user data"""
    # Placeholder - replace with actual Google Sheets lookup
    # Example implementation:
    # client = get_google_sheets_client()
    # sheet = client.open('Spikeball Interest Form').sheet1
    # records = sheet.get_all_records()
    # for idx, record in enumerate(records):
    #     if record.get('Email') == email:
    #         return {'name': record.get('Name'), 'row': idx + 2, 'id': record.get('ID')}
    # return None
    
    # Demo data for testing
    demo_users = {
        'john@example.com': {'name': 'John Doe', 'row': 2, 'id': 'player1'},
        'jane@example.com': {'name': 'Jane Smith', 'row': 3, 'id': 'player2'},
        'test@test.com': {'name': 'Test User', 'row': 4, 'id': 'player3'}
    }
    return demo_users.get(email)

def get_tournament_rounds(user_id):
    """Get tournament rounds for a specific user"""
    # Placeholder - replace with actual Google Sheets lookup
    # Demo data
    rounds_data = [
        {'Round': 1, 'Net Number': 1, 'id1': 'player1', 'id2': 'player2', 'id3': 'player3', 'id4': 'player4'},
        {'Round': 2, 'Net Number': 1, 'id1': 'player1', 'id2': 'player3', 'id3': 'player2', 'id4': 'player4'},
        {'Round': 3, 'Net Number': 2, 'id1': 'player1', 'id2': 'player4', 'id3': 'player2', 'id4': 'player3'}
    ]
    
    # Filter rounds where user is one of the 4 players
    user_rounds = []
    for round_data in rounds_data:
        if user_id in [round_data['id1'], round_data['id2'], round_data['id3'], round_data['id4']]:
            user_rounds.append(round_data)
    
    return user_rounds

def submit_results(round_data, results):
    """Submit results to Google Sheets"""
    # Placeholder - replace with actual Google Sheets write
    print(f"Submitting results: {round_data}, {results}")
    return True

# App layout
app.layout = dbc.Container([
    dcc.Store(id='user-data'),
    dcc.Store(id='current-round-data'),
    dcc.Interval(id='refresh-interval', interval=10000, n_intervals=0),  # Refresh every 10 seconds
    
    html.Div(id='page-content'),
], fluid=True, className="px-3 py-4")

# Login page layout
def create_login_page():
    return dbc.Row([
        dbc.Col([
            html.H1("Welcome to Spikeball!", 
                   className="text-center mb-4 display-4 fw-bold text-primary"),
            
            dbc.Card([
                dbc.CardBody([
                    html.P("If you have already filled out our interest form, please fill in your email used in the form:", 
                          className="mb-3 fs-6"),
                    
                    dbc.InputGroup([
                        dbc.Input(id="email-input", placeholder="Enter your email", 
                                type="email", className="form-control-lg"),
                        dbc.Button("Enter", id="login-button", color="primary", 
                                 className="btn-lg")
                    ], className="mb-3"),
                    
                    html.Div(id="login-error", className="text-danger mb-3"),
                    
                    html.Hr(),
                    
                    html.P("If you haven't filled out the form, please fill it out:", 
                          className="mb-3 fs-6"),
                    
                    dbc.Button("Fill Out Interest Form", 
                             href="https://forms.google.com/your-form-link",
                             color="success", size="lg", className="w-100",
                             external_link=True)
                ])
            ], className="shadow")
        ], width=12, md=8, lg=6, className="mx-auto")
    ])

# Tournament page layout
def create_tournament_page(user_data, round_data):
    if not round_data:
        return dbc.Row([
            dbc.Col([
                html.H1("Assigned Groupings", className="text-center mb-4 text-primary"),
                dbc.Alert("No rounds available yet. Please wait for the tournament to begin.", 
                         color="info", className="text-center")
            ], width=12)
        ])
    
    round_num = round_data['Round']
    net_num = round_data['Net Number']
    id1, id2, id3, id4 = round_data['id1'], round_data['id2'], round_data['id3'], round_data['id4']
    
    return dbc.Row([
        dbc.Col([
            html.H1("Assigned Groupings", className="text-center mb-4 text-primary"),
            
            dbc.Card([
                dbc.CardBody([
                    html.H4(f"Round Number: {round_num}", className="text-center mb-4 text-info"),
                    html.H6(f"Net Number: {net_num}", className="text-center mb-4 text-secondary"),
                    
                    # Match 1: id1/id2 vs id3/id4
                    dbc.Row([
                        dbc.Col([
                            dbc.RadioItems(
                                id="match1-radio",
                                options=[
                                    {"label": f"{id1} / {id2}", "value": "left"},
                                    {"label": f"{id3} / {id4}", "value": "right"}
                                ],
                                inline=True,
                                className="d-flex justify-content-between align-items-center"
                            )
                        ], width=12)
                    ], className="mb-3 p-3 border rounded"),
                    
                    # Match 2: id1/id3 vs id2/id4  
                    dbc.Row([
                        dbc.Col([
                            dbc.RadioItems(
                                id="match2-radio",
                                options=[
                                    {"label": f"{id1} / {id3}", "value": "left"},
                                    {"label": f"{id2} / {id4}", "value": "right"}
                                ],
                                inline=True,
                                className="d-flex justify-content-between align-items-center"
                            )
                        ], width=12)
                    ], className="mb-3 p-3 border rounded"),
                    
                    # Match 3: id1/id4 vs id2/id3
                    dbc.Row([
                        dbc.Col([
                            dbc.RadioItems(
                                id="match3-radio",
                                options=[
                                    {"label": f"{id1} / {id4}", "value": "left"},
                                    {"label": f"{id2} / {id3}", "value": "right"}
                                ],
                                inline=True,
                                className="d-flex justify-content-between align-items-center"
                            )
                        ], width=12)
                    ], className="mb-4 p-3 border rounded"),
                    
                    html.Div(id="submit-error", className="text-danger mb-3"),
                    
                    dbc.Button("Submit Results", id="submit-button", color="success", 
                             size="lg", className="w-100 mb-3"),
                    
                    html.Div(id="submit-status")
                ])
            ], className="shadow")
        ], width=12, md=10, lg=8, className="mx-auto")
    ])

# Callback for page routing and login
@app.callback(
    [Output('page-content', 'children'),
     Output('user-data', 'data'),
     Output('current-round-data', 'data'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('refresh-interval', 'n_intervals')],
    [State('email-input', 'value'),
     State('user-data', 'data'),
     State('current-round-data', 'data')]
)
def handle_navigation(n_clicks, n_intervals, email, user_data, current_round_data):
    ctx = callback_context
    
    # Initial page load or refresh
    if not ctx.triggered or not user_data:
        if n_clicks and email:
            # Login attempt
            user_info = check_user_exists(email)
            if user_info:
                # Get current round data
                rounds = get_tournament_rounds(user_info['id'])
                latest_round = max(rounds, key=lambda x: x['Round']) if rounds else None
                
                return (create_tournament_page(user_info, latest_round), 
                       user_info, latest_round, "")
            else:
                return (create_login_page(), None, None, 
                       "User doesn't exist. Please check your email or fill out the interest form.")
        else:
            return create_login_page(), None, None, ""
    
    # User is logged in, check for new rounds
    if user_data and ctx.triggered[0]['prop_id'] == 'refresh-interval.n_intervals':
        rounds = get_tournament_rounds(user_data['id'])
        latest_round = max(rounds, key=lambda x: x['Round']) if rounds else None
        
        # Check if there's a new round
        if latest_round and (not current_round_data or latest_round['Round'] > current_round_data['Round']):
            return (create_tournament_page(user_data, latest_round), 
                   user_data, latest_round, "")
    
    # Return current state if no changes
    return (create_tournament_page(user_data, current_round_data) if user_data else create_login_page(), 
           user_data, current_round_data, "")

# Callback for input styling on error
@app.callback(
    Output('email-input', 'className'),
    [Input('login-error', 'children')]
)
def update_input_style(error_message):
    if error_message:
        return "form-control-lg border-danger"
    return "form-control-lg"

# Callback for submit button
@app.callback(
    [Output('submit-error', 'children'),
     Output('submit-status', 'children')],
    [Input('submit-button', 'n_clicks')],
    [State('match1-radio', 'value'),
     State('match2-radio', 'value'),
     State('match3-radio', 'value'),
     State('current-round-data', 'data')]
)
def handle_submit(n_clicks, match1, match2, match3, round_data):
    if not n_clicks or not round_data:
        return "", ""
    
    # Check if all matches have selections
    if not all([match1, match2, match3]):
        return "Please select a winner for each match.", ""
    
    # Convert selections to binary format (1 for left, 0 for right)
    results = [
        1 if match1 == "left" else 0,
        1 if match2 == "left" else 0,
        1 if match3 == "left" else 0
    ]
    
    # Submit results
    success = submit_results(round_data, results)
    
    if success:
        return "", dbc.Alert("Thank you for submitting! Please wait for the next round.", 
                           color="success", className="text-center")
    else:
        return "Error submitting results. Please try again.", ""

# Custom CSS for mobile optimization
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            
            .container-fluid {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 15px;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            
            .card {
                border: none;
                border-radius: 15px;
            }
            
            .btn {
                border-radius: 10px;
                font-weight: 600;
            }
            
            .form-control, .form-control-lg {
                border-radius: 10px;
                border: 2px solid #e9ecef;
            }
            
            .form-control:focus, .form-control-lg:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
            }
            
            .border-danger {
                border-color: #dc3545 !important;
            }
            
            @media (max-width: 768px) {
                .display-4 {
                    font-size: 2rem;
                }
                
                .btn-lg {
                    padding: 0.75rem 1.5rem;
                }
                
                .container-fluid {
                    margin-top: 10px;
                    margin-bottom: 10px;
                    border-radius: 10px;
                }
            }
            
            .form-check-input:checked {
                background-color: #667eea;
                border-color: #667eea;
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

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)