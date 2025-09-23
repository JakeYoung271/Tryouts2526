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
            html.H1("Welcome to Our Platform", className="text-center mb-4"),
            html.P("Your one-stop solution for amazing services", 
                   className="lead text-center text-muted")
        ])
    ], className="py-5"),
    
    # Hero section
    dbc.Row([
        dbc.Col([
            html.H2("Get Started Today"),
            html.P("Discover the power of our platform with these amazing features."),
            dbc.Button("Learn More", color="primary", size="lg", className="me-2"),
            dbc.Button("Sign Up", color="outline-primary", size="lg")
        ], md=6),
        dbc.Col([
            html.Img(src="/assets/hero-image.png", className="img-fluid")
        ], md=6)
    ], className="py-5 align-items-center"),
    
    # Features section
    dbc.Row([
        dbc.Col([
            html.H3("Features"),
            dbc.Row([
                dbc.Col([
                    html.H5("Feature 1"),
                    html.P("Description of your first amazing feature.")
                ], md=4),
                dbc.Col([
                    html.H5("Feature 2"),
                    html.P("Description of your second amazing feature.")
                ], md=4),
                dbc.Col([
                    html.H5("Feature 3"),
                    html.P("Description of your third amazing feature.")
                ], md=4)
            ])
        ])
    ], className="py-5"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("© 2024 Your Company. All rights reserved.", 
                   className="text-center text-muted")
        ])
    ])
], fluid=True)

if __name__ == "__main__":
    app.run_server(debug=True)