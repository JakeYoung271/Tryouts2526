import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import pandas as pd
import requests
from io import StringIO
import json
import time
import csv
from datetime import datetime

# Initialize Dash app with Bootstrap theme for mobile responsiveness
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Spikeball Tournament"
app.config.suppress_callback_exceptions = True

# Google Sheets configuration - Using public CSV export URLs
USER_SHEET_ID = '1KmJBO5oKwygn-2AzwX-hS1wGeQMmLwyizFqtsSZo7_w'
USER_DATA_GID = '900351397'

TOURNAMENT_SHEET_ID = '1srq_lb7-c601uE3gSumhWltxsjXi3HRUVRHpdkgLu-w'
TOURNAMENT_GID = '1153687443'

RESULTS_SHEET_ID = '1vuQ394gU_CSNEO-U0ZFVRTNC1jIWV1BT_yjGqoQQPOk'
RESULTS_GID = '0'

# CSV export URLs for public sheets
USER_DATA_CSV_URL = f"https://docs.google.com/spreadsheets/d/{USER_SHEET_ID}/export?format=csv&gid={USER_DATA_GID}"
TOURNAMENT_ROUNDS_CSV_URL = f"https://docs.google.com/spreadsheets/d/{TOURNAMENT_SHEET_ID}/export?format=csv&gid={TOURNAMENT_GID}"
RESULTS_CSV_URL = f"https://docs.google.com/spreadsheets/d/{RESULTS_SHEET_ID}/export?format=csv&gid={RESULTS_GID}"

import requests
from io import StringIO

def read_public_sheet_as_df(csv_url):
    """Read a public Google Sheet as a pandas DataFrame"""
    try:
        response = requests.get(csv_url, timeout=10)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df
    except Exception as e:
        print(f"Error reading sheet: {e}")
        return None

def check_user_exists(email):
    """Check if user exists in Google Sheets and return user data"""
    try:
        # Read the user data sheet
        df = read_public_sheet_as_df(USER_DATA_CSV_URL)
        
        if df is None:
            print("ERROR: cant read user data or nonexistent")
            return None
        
        # Clean up column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        
        # Search for user by email
        # Column mapping: Timestamp, UCLA email, First and Last name
        for idx, row in df.iterrows():
            user_email = str(row.get('UCLA email', '')).strip().lower()
            if user_email == email.lower():
                full_name = str(row.get('First and Last name', '')).strip()
                # Create a simple ID from the name (remove spaces, convert to lowercase)
                user_id = full_name.lower().replace(' ', '_').replace('.', '') if full_name else f'user_{idx+2}'
                print(full_name)
                print(idx + 2)
                print(user_id)
                print(email)
                return {
                    'name': full_name,
                    'row': idx + 2,  # +2 because pandas is 0-indexed and we account for header row
                    'id': user_id,
                    'email': user_email
                }
        
        return None
        
    except Exception as e:
        print(f"Error checking user: {e}")
        return None
    
def get_user_name(user_id_list):
    try:
        # Read the user data sheet
        df = read_public_sheet_as_df(USER_DATA_CSV_URL)
        
        if df is None:
            print("ERROR: cant read user data or nonexistent")
            return user_id_list  # Return the original IDs if we can't read the sheet
        df.columns = df.columns.str.strip()
        records = df.to_dict('records')
        id_to_name_mapping = {}
        for idx, record in enumerate(records):
            try:
                full_name_value = record.get('First and Last name', '')
                if pd.isna(full_name_value) or full_name_value is None:
                    full_name = ''
                else:
                    full_name = str(full_name_value).strip()
                if full_name:
                    row_user_id = full_name.lower().replace(' ', '_').replace('.', '')
                else:
                    row_user_id = f'user_{idx+2}'
                id_to_name_mapping[idx + 2] = full_name if full_name else row_user_id
                    
            except Exception as row_error:
                print(f"Error processing row {idx}: {row_error}")
                continue

        result_names = []
        for user_id in user_id_list:
            if user_id in id_to_name_mapping:
                result_names.append(id_to_name_mapping[user_id])
            else:
                result_names.append(user_id)
        
        return result_names
        
    except Exception as e:
        print(f"Error getting real names: {e}")
        return user_id_list

def get_tournament_rounds(user_id):
    """Get tournament rounds for a specific user"""
    try:
        # Read the tournament rounds sheet
        df = read_public_sheet_as_df(TOURNAMENT_ROUNDS_CSV_URL)
        
        if df is None:
            print("ERROR: cant read user data or nonexistent")
            return None
        else:
            # Clean up column names (remove extra spaces)
            df.columns = df.columns.str.strip()
            
            # Convert DataFrame to list of dictionaries
            rounds_data = df.to_dict('records')
        
        # Filter rounds where user is one of the 4 players
        user_rounds = []
        for round_data in rounds_data:
            # Convert all values to strings for comparison (handle NaN values)
            id1 = int(str(round_data.get('id1', '')).strip())
            id2 = int(str(round_data.get('id2', '')).strip())
            id3 = int(str(round_data.get('id3', '')).strip())
            id4 = int(str(round_data.get('id4', '')).strip())
            if user_id in [id1, id2, id3, id4]:
                # Ensure all required fields are present and clean
                clean_round = {
                    'Round': round_data.get('Round', 0),
                    'Net Number': round_data.get('Net Number', 0),
                    'id1': id1,
                    'id2': id2,
                    'id3': id3,
                    'id4': id4
                }
                user_rounds.append(clean_round)
        return user_rounds
        
    except Exception as e:
        print(f"Error getting tournament rounds: {e}")
        return None

def submit_results(round_data, results, username):
    """Submit results to Google Sheets"""
    try:
        # Since we can't directly write to public Google Sheets via CSV export,
        # we need an alternative approach. Here are the options:
        
        # Prepare the data that would be submitted

        form_url = "https://docs.google.com/forms/d/e/1FAIpQLSe4-6_u7UkQ6bmrKQj8mxcqgDF82v6DDjDA2pk3WaJKIyzc8g/formResponse"
        new_row_data = {
            'entry.175605993': round_data['Round'],
            'entry.38731083': round_data['Net Number'],
            'entry.1960261060': round_data['id1'],
            'entry.791831527': round_data['id2'],
            'entry.40405346': round_data['id3'],
            'entry.751547352': round_data['id4'],
            'entry.1089736874': results[0],
            'entry.1449374216': results[1],
            'entry.1388039134': results[2],
            'entry.2146235891': username
        }
        #entry.38731083

        print(f"Results to submit: {new_row_data}")
        r = requests.post(form_url, data=new_row_data, timeout=10)
        if r.status_code != 200 and r.status_code != 302:
            print("Failed:", r.status_code)
        time.sleep(0.15)  # be gentle; Forms may throttle
        
        print("✅ Results logged successfully (using demo mode)")
        return True
        
    except Exception as e:
        print(f"Error submitting results: {e}")
        return False

# App layout - Include all components from start to avoid callback issues
app.layout = dbc.Container([
    dcc.Store(id='user-data'),
    dcc.Store(id='current-round-data'),
    dcc.Store(id='page-state', data='login'),  # Track which page we're on
    dcc.Store(id='submit-state', data={'submitted': False, 'round': None}),
    dcc.Interval(id='refresh-interval', interval=10000, n_intervals=0),
    
    # Login page components
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Welcome to Spikeball!", 
                       className="text-center mb-4 display-4 fw-bold text-primary"),
                
                dbc.Card([
                    dbc.CardBody([
                        html.P("If you have already filled out our interest form, please fill in your email used in the form:", 
                              className="mb-3 fs-6"),
                        
                        dbc.InputGroup([
                            dbc.Input(id="email-input", placeholder="Enter your UCLA email", 
                                    type="email", className="form-control-lg"),
                            dbc.Button("Enter", id="login-button", color="primary", 
                                     className="btn-lg")
                        ], className="mb-3"),
                        
                        html.Div(id="login-error", className="text-danger mb-3"),
                        
                        html.Hr(),
                        
                        html.P("If you haven't filled out the form, please fill it out:", 
                              className="mb-3 fs-6"),
                        
                        dbc.Button("Fill Out Interest Form", 
                                 href="https://docs.google.com/forms/u/1/d/e/1FAIpQLSdY8THwf05cBQXt5Zih-4nsAAXl64vNoqCpgPu4ltTnylX9bg/viewform",
                                 color="success", size="lg", className="w-100",
                                 external_link=True)
                    ])
                ], className="shadow")
            ], width=12, md=8, lg=6, className="mx-auto")
        ])
    ], id="login-page", style={'display': 'block'}),
    
    # Tournament page components
    html.Div([
        dbc.Row([
            dbc.Col([
                html.H1("Assigned Groupings", className="text-center mb-4 text-primary"),
                html.H4("Please select the winners of each match", className="text-center mb-4 text-secondary"),
                
                html.Div(id="tournament-content", children=[
                    dbc.Alert("No rounds available yet. Please wait for the tournament to begin.", 
                             color="info", className="text-center")
                ])
            ], width=12, md=10, lg=8, className="mx-auto")
        ])
    ], id="tournament-page", style={'display': 'none'}),
    
], fluid=True, className="px-3 py-4")

# Tournament content creation
def create_tournament_content(user_data, round_data, submit_state=None):
    if not round_data:
        return dbc.Alert("No rounds available yet. Please wait for the tournament to begin.", 
                        color="info", className="text-center")
    
    round_num = round_data['Round']
    net_num = round_data['Net Number']
    ids = get_user_name([round_data['id1'], round_data['id2'], round_data['id3'], round_data['id4']])
    is_submitted = (submit_state and 
                   submit_state.get('submitted') and 
                   submit_state.get('round') == round_num)
    return dbc.Card([
        dbc.CardBody([
            html.H4(f"Round Number: {round_num}", className="text-center mb-4 text-info"),
            html.H6(f"Net Number: {net_num}", className="text-center mb-4 text-secondary"),
            
            # Match 1 with inline radio buttons
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("Match 1: ", className="fw-bold me-2"),
                        dbc.RadioItems(
                            id="match1-radio",
                            options=[
                                {"label": f"{ids[0]}/{ids[1]}", "value": "left"},
                                {"label": f"{ids[2]}/{ids[3]}", "value": "right"}
                            ],
                            inline=True,
                            className="d-inline-flex gap-3"
                        )
                    ], className="mb-3 text-center")
                ], width=12)
            ]),
            
            # Match 2 with inline radio buttons
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("Match 2: ", className="fw-bold me-2"),
                        dbc.RadioItems(
                            id="match2-radio",
                            options=[
                                {"label": f"{ids[0]}/{ids[2]}", "value": "left"},
                                {"label": f"{ids[1]}/{ids[3]}", "value": "right"}
                            ],
                            inline=True,
                            className="d-inline-flex gap-3"
                        )
                    ], className="mb-3 text-center")
                ], width=12)
            ]),
            
            # Match 3 with inline radio buttons
            dbc.Row([
                dbc.Col([
                    html.Div([
                        html.Span("Match 3: ", className="fw-bold me-2"),
                        dbc.RadioItems(
                            id="match3-radio",
                            options=[
                                {"label": f"{ids[0]}/{ids[3]}", "value": "left"},
                                {"label": f"{ids[1]}/{ids[2]}", "value": "right"}
                            ],
                            inline=True,
                            className="d-inline-flex gap-3"
                        )
                    ], className="mb-4 text-center")
                ], width=12)
            ]),
            
            # Submit button
            dbc.Row([
                dbc.Col([
                    dbc.Button("Submit Results", id="submit-button", color="success", 
                             size="lg", className="w-100 mb-3", disabled=is_submitted) if not is_submitted
                    else dbc.Alert("Thank you for submitting! Please wait for the next round.", 
                                 color="success", className="text-center")
                ], width=12)
            ]),
            
            # Status and error messages
            html.Div(id="submit-error", className="text-danger mb-3"),
            html.Div(id="submit-status")
        ])
    ], className="shadow")

# Callback for page navigation and login
@app.callback(
    [Output('login-page', 'style'),
     Output('tournament-page', 'style'),
     Output('tournament-content', 'children'),
     Output('user-data', 'data'),
     Output('current-round-data', 'data'),
     Output('login-error', 'children')],
    [Input('login-button', 'n_clicks'),
     Input('refresh-interval', 'n_intervals'),
     Input('submit-state', 'data')],
    [State('email-input', 'value'),
     State('user-data', 'data'),
     State('current-round-data', 'data')]
)
def handle_navigation(n_clicks, n_intervals,  submit_state, email, user_data, current_round_data):
    ctx = callback_context
    
    # Default styles
    login_style = {'display': 'block'}
    tournament_style = {'display': 'none'}
    
    # Initial page load or refresh
    if not ctx.triggered or not user_data:
        if n_clicks and email:
            # Login attempt
            user_info = check_user_exists(email)
            if user_info:
                # Get current round data
                rounds = get_tournament_rounds(user_info['row'])
                latest_round = max(rounds, key=lambda x: x['Round']) if rounds else None
                
                if latest_round:
                    # Show tournament page
                    return (
                        {'display': 'none'},  # login page
                        {'display': 'block'},  # tournament page
                        create_tournament_content(user_info, latest_round, submit_state),  # tournament content
                        user_info,  # user data
                        latest_round,  # round data
                        ""  # login error
                    )
                else:
                    # User exists but no rounds yet
                    return (
                        {'display': 'none'},  # login page
                        {'display': 'block'},  # tournament page
                        dbc.Alert("No rounds available yet. Please wait for the tournament to begin.", color="info", className="text-center"),
                        user_info, None, ""
                    )
            else:
                # User doesn't exist
                return (
                    login_style, tournament_style,
                    dbc.Alert("No rounds available.", color="info"),
                    None, None, "User doesn't exist. Please check your email or fill out the interest form."
                )
        else:
            # Show login page
            return (
                login_style, tournament_style,
                dbc.Alert("No rounds available.", color="info"),
                None, None, ""
            )
    
    # User is logged in, check for new rounds
    if user_data:
        triggered_id = ctx.triggered[0]['prop_id'] if ctx.triggered else None
        if triggered_id == 'refresh-interval.n_intervals':
            rounds = get_tournament_rounds(user_data['row'])
            latest_round = max(rounds, key=lambda x: x['Round']) if rounds else None
            
            # Check if there's a new round
            if latest_round and (not current_round_data or latest_round['Round'] > current_round_data['Round']):
                return (
                    {'display': 'none'}, {'display': 'block'},
                    create_tournament_content(user_data, latest_round, submit_state),
                    user_data, latest_round, ""
                )
            else:
                # No new rounds, stay on current page
                if current_round_data:
                    return (
                        {'display': 'none'}, {'display': 'block'},
                        create_tournament_content(user_data, current_round_data, submit_state),
                        user_data, current_round_data, ""
                    )
                else:
                    return (
                        {'display': 'none'}, {'display': 'block'},
                        dbc.Alert("No rounds available yet. Please wait for the tournament to begin.", color="info", className="text-center"),
                        user_data, None, ""
                    )
        elif triggered_id == 'submit-state.data':
            if current_round_data:
                return (
                    {'display': 'none'}, {'display': 'block'},
                    create_tournament_content(user_data, current_round_data, submit_state),
                    user_data, current_round_data, ""
                )
    
    # Return current state
    current_content = create_tournament_content(user_data, current_round_data, submit_state) if user_data and current_round_data else dbc.Alert("No rounds available.", color="info")
    
    if user_data:
        return (
            {'display': 'none'}, {'display': 'block'},
            current_content, user_data, current_round_data, ""
        )
    else:
        return (
            login_style, tournament_style, current_content,
            user_data, current_round_data, ""
        )

# Callback for input styling on error
@app.callback(
    Output('email-input', 'className'),
    [Input('login-error', 'children')],
    prevent_initial_call=True
)
def update_input_style(error_message):
    if error_message:
        return "form-control-lg border-danger"
    return "form-control-lg"

# Callback for submit button
@app.callback(
    [Output('submit-error', 'children'),
     Output('submit-status', 'children'),
     Output('submit-state', 'data')],
    [Input('submit-button', 'n_clicks')],
    [State('match1-radio', 'value'),
     State('match2-radio', 'value'),
     State('match3-radio', 'value'),
     State('current-round-data', 'data'),
     State('user-data', 'data')]
)
def handle_submit(n_clicks, match1, match2, match3, round_data, user_data):
    if not n_clicks or not round_data:
        return "", "", {'submitted': False, 'round': None}
    
    # Check if all matches have selections
    if not all([match1, match2, match3]):
        return "Please select a winner for each match.", "", {'submitted': False, 'round': None}
    
    # Convert selections to binary format (1 for left, 0 for right)
    results = [
        1 if match1 == "left" else 0,
        1 if match2 == "left" else 0,
        1 if match3 == "left" else 0
    ]

    print(user_data)
    
    # Submit results
    success = submit_results(round_data, results, user_data['row'])
    
    if success:
        return "", "", {'submitted': True, 'round': round_data['Round']}
    else:
        return "Error submitting results. Please try again.", "", {'submitted': False, 'round': None}

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
    app.run(debug=False, host='0.0.0.0', port=8050)