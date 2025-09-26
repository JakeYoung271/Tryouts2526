import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = dbc.Container([
    # Header section
    dbc.Row([
        dbc.Col([
            dbc.NavbarSimple(
                brand="Dashboard",
                brand_href="#",
                color="primary",
                dark=True,
                className="mb-4"
            )
        ])
    ]),
    
    # Main body section
    dbc.Row([
        dbc.Col([
            # Sidebar/Navigation (optional)
            dbc.Card([
                dbc.CardBody([
                    html.H5("Navigation", className="card-title"),
                    dbc.Nav([
                        dbc.NavLink("Overview", href="#", active="exact"),
                        dbc.NavLink("Analytics", href="#"),
                        dbc.NavLink("Reports", href="#"),
                        dbc.NavLink("Settings", href="#"),
                    ], vertical=True, pills=True)
                ])
            ])
        ], md=3),
        
        dbc.Col([
            # Main content area
            dbc.Card([
                dbc.CardHeader([
                    html.H4("Dashboard Overview", className="mb-0")
                ]),
                dbc.CardBody([
                    # Content placeholder
                    html.Div([
                        html.H5("Welcome to your Dashboard"),
                        html.P("This is the main content area where you can display charts, tables, and other dashboard components."),
                        
                        # Example content sections
                        dbc.Row([
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Metric 1", className="card-subtitle mb-2 text-muted"),
                                        html.H3("1,234", className="card-title text-primary"),
                                        html.P("Some description", className="card-text")
                                    ])
                                ])
                            ], md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Metric 2", className="card-subtitle mb-2 text-muted"),
                                        html.H3("5,678", className="card-title text-success"),
                                        html.P("Some description", className="card-text")
                                    ])
                                ])
                            ], md=4),
                            dbc.Col([
                                dbc.Card([
                                    dbc.CardBody([
                                        html.H6("Metric 3", className="card-subtitle mb-2 text-muted"),
                                        html.H3("9,012", className="card-title text-info"),
                                        html.P("Some description", className="card-text")
                                    ])
                                ])
                            ], md=4)
                        ], className="mb-4"),
                        
                        # Placeholder for charts or additional content
                        dbc.Card([
                            dbc.CardHeader("Chart Area"),
                            dbc.CardBody([
                                html.P("This is where you can add charts, graphs, or other visualizations."),
                                html.Div(
                                    "Chart placeholder - add your Plotly graphs here",
                                    style={
                                        'height': '300px',
                                        'backgroundColor': '#f8f9fa',
                                        'border': '2px dashed #dee2e6',
                                        'display': 'flex',
                                        'alignItems': 'center',
                                        'justifyContent': 'center',
                                        'color': '#6c757d'
                                    }
                                )
                            ])
                        ])
                    ])
                ])
            ])
        ], md=9)
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)
