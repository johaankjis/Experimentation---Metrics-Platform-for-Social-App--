"""
Main Plotly Dash application for experimentation platform.
Provides interactive visualizations and real-time experiment monitoring.
"""

import dash
from dash import dcc, html, Input, Output, State, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ab_framework.assignment import UserAssignment, ExperimentConfig, ExperimentStatus
from src.ab_framework.stats_tests import ABTestAnalyzer, TestType
from src.ab_framework.metrics import MetricRegistry, MetricComputer

# Initialize Dash app with Bootstrap theme
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    title="Experimentation Platform"
)

# Color scheme
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
    'background': '#F8F9FA',
    'card': '#FFFFFF',
    'text': '#212529',
    'text_secondary': '#6C757D'
}

# ============================================================================
# LAYOUT COMPONENTS
# ============================================================================

def create_navbar():
    """Create navigation bar"""
    return dbc.Navbar(
        dbc.Container([
            dbc.Row([
                dbc.Col(html.H3("🧪 Experimentation Platform", className="text-white mb-0")),
            ], align="center", className="g-0"),
            dbc.Nav([
                dbc.NavItem(dbc.NavLink("Dashboard", href="/", active="exact")),
                dbc.NavItem(dbc.NavLink("Experiments", href="/experiments", active="exact")),
                dbc.NavItem(dbc.NavLink("Metrics", href="/metrics", active="exact")),
                dbc.NavItem(dbc.NavLink("Analysis", href="/analysis", active="exact")),
            ], navbar=True),
        ], fluid=True),
        color=COLORS['primary'],
        dark=True,
        className="mb-4"
    )


def create_stat_card(title, value, subtitle, icon, color):
    """Create a statistics card"""
    return dbc.Card([
        dbc.CardBody([
            html.Div([
                html.Div([
                    html.H6(title, className="text-muted mb-2"),
                    html.H3(value, className="mb-0", style={'color': color}),
                    html.P(subtitle, className="text-muted small mb-0 mt-1"),
                ], style={'flex': '1'}),
                html.Div([
                    html.I(className=f"bi bi-{icon}", style={
                        'fontSize': '2.5rem',
                        'color': color,
                        'opacity': '0.3'
                    })
                ], style={'marginLeft': '1rem'})
            ], style={'display': 'flex', 'alignItems': 'center'})
        ])
    ], className="shadow-sm h-100")


def create_dashboard_layout():
    """Create main dashboard layout"""
    return dbc.Container([
        # Header stats
        dbc.Row([
            dbc.Col([
                create_stat_card(
                    "Active Experiments",
                    "5",
                    "+2 from last week",
                    "flask",
                    COLORS['primary']
                )
            ], md=3),
            dbc.Col([
                create_stat_card(
                    "Significant Results",
                    "3",
                    "60% success rate",
                    "graph-up-arrow",
                    COLORS['success']
                )
            ], md=3),
            dbc.Col([
                create_stat_card(
                    "Total Users",
                    "125K",
                    "+15% this month",
                    "people",
                    COLORS['secondary']
                )
            ], md=3),
            dbc.Col([
                create_stat_card(
                    "Guardrail Violations",
                    "1",
                    "Requires attention",
                    "exclamation-triangle",
                    COLORS['warning']
                )
            ], md=3),
        ], className="mb-4"),
        
        # Main content
        dbc.Row([
            # Left column - Experiment list
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Active Experiments", className="mb-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-experiments",
                            children=[html.Div(id="experiment-list")],
                            type="default"
                        )
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Recent Activity", className="mb-0")),
                    dbc.CardBody([
                        html.Div(id="activity-feed")
                    ])
                ], className="shadow-sm")
            ], md=4),
            
            # Right column - Charts
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.H5("Experiment Performance", className="mb-0"),
                            dbc.Select(
                                id="experiment-selector",
                                options=[
                                    {"label": "Homepage Redesign", "value": "homepage_redesign_v1"},
                                    {"label": "Checkout Flow", "value": "checkout_flow_v2"},
                                ],
                                value="homepage_redesign_v1",
                                style={'width': '250px'}
                            )
                        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'})
                    ]),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-performance",
                            children=[dcc.Graph(id="performance-chart")],
                            type="default"
                        )
                    ])
                ], className="shadow-sm mb-4"),
                
                dbc.Card([
                    dbc.CardHeader(html.H5("Statistical Significance", className="mb-0")),
                    dbc.CardBody([
                        dcc.Loading(
                            id="loading-significance",
                            children=[dcc.Graph(id="significance-chart")],
                            type="default"
                        )
                    ])
                ], className="shadow-sm")
            ], md=8),
        ]),
        
        # Refresh interval
        dcc.Interval(
            id='interval-component',
            interval=30*1000,  # Update every 30 seconds
            n_intervals=0
        )
    ], fluid=True)


def create_experiments_layout():
    """Create experiments page layout"""
    return dbc.Container([
        dbc.Row([
            dbc.Col([
                html.H2("Experiment Management"),
                html.P("View and manage all experiments", className="text-muted")
            ], md=8),
            dbc.Col([
                dbc.Button("New Experiment", color="primary", className="float-end")
            ], md=4)
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Div(id="experiments-table")
                    ])
                ], className="shadow-sm")
            ])
        ])
    ], fluid=True)


def create_analysis_layout():
    """Create detailed analysis page layout"""
    return dbc.Container([
        html.H2("Experiment Analysis", className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H5("Select Experiment", className="mb-0")),
                    dbc.CardBody([
                        dbc.Select(
                            id="analysis-experiment-selector",
                            options=[
                                {"label": "Homepage Redesign", "value": "homepage_redesign_v1"},
                                {"label": "Checkout Flow", "value": "checkout_flow_v2"},
                            ],
                            value="homepage_redesign_v1"
                        ),
                        html.Hr(),
                        html.Div(id="experiment-details")
                    ])
                ], className="shadow-sm")
            ], md=3),
            
            dbc.Col([
                dbc.Tabs([
                    dbc.Tab(label="Metrics", tab_id="metrics-tab"),
                    dbc.Tab(label="Statistical Tests", tab_id="stats-tab"),
                    dbc.Tab(label="Time Series", tab_id="timeseries-tab"),
                    dbc.Tab(label="Guardrails", tab_id="guardrails-tab"),
                ], id="analysis-tabs", active_tab="metrics-tab"),
                html.Div(id="analysis-content", className="mt-3")
            ], md=9)
        ])
    ], fluid=True)


# ============================================================================
# MAIN LAYOUT
# ============================================================================

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(),
    html.Div(id='page-content')
])


# ============================================================================
# CALLBACKS
# ============================================================================

@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """Route to different pages"""
    if pathname == '/experiments':
        return create_experiments_layout()
    elif pathname == '/analysis':
        return create_analysis_layout()
    elif pathname == '/metrics':
        return html.Div("Metrics page - Coming soon")
    else:
        return create_dashboard_layout()


@callback(
    Output('experiment-list', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_experiment_list(n):
    """Update list of active experiments"""
    experiments = [
        {
            'name': 'Homepage Redesign',
            'id': 'homepage_redesign_v1',
            'status': 'active',
            'progress': 75,
            'users': '45K',
            'significant': True
        },
        {
            'name': 'Checkout Flow',
            'id': 'checkout_flow_v2',
            'status': 'active',
            'progress': 60,
            'users': '32K',
            'significant': False
        },
        {
            'name': 'Search Algorithm',
            'id': 'search_algo_v3',
            'status': 'active',
            'progress': 30,
            'users': '18K',
            'significant': False
        },
    ]
    
    items = []
    for exp in experiments:
        badge_color = "success" if exp['significant'] else "secondary"
        badge_text = "Significant" if exp['significant'] else "Running"
        
        items.append(
            dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.H6(exp['name'], className="mb-1"),
                        dbc.Badge(badge_text, color=badge_color, className="mb-2"),
                    ]),
                    html.P(f"{exp['users']} users", className="text-muted small mb-2"),
                    dbc.Progress(value=exp['progress'], className="mb-2", style={'height': '8px'}),
                    html.Small(f"{exp['progress']}% complete", className="text-muted")
                ])
            ], className="mb-2")
        )
    
    return items


@callback(
    Output('activity-feed', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_activity_feed(n):
    """Update recent activity feed"""
    activities = [
        {'time': '5 min ago', 'text': 'Homepage Redesign reached significance', 'icon': 'check-circle', 'color': COLORS['success']},
        {'time': '1 hour ago', 'text': 'Checkout Flow started', 'icon': 'play-circle', 'color': COLORS['primary']},
        {'time': '3 hours ago', 'text': 'Guardrail violation detected', 'icon': 'exclamation-triangle', 'color': COLORS['warning']},
        {'time': '1 day ago', 'text': 'Search Algorithm completed', 'icon': 'flag', 'color': COLORS['secondary']},
    ]
    
    items = []
    for activity in activities:
        items.append(
            html.Div([
                html.Div([
                    html.I(className=f"bi bi-{activity['icon']}", style={
                        'color': activity['color'],
                        'marginRight': '10px',
                        'fontSize': '1.2rem'
                    }),
                    html.Div([
                        html.P(activity['text'], className="mb-0 small"),
                        html.Small(activity['time'], className="text-muted")
                    ])
                ], style={'display': 'flex', 'alignItems': 'center'}),
                html.Hr(className="my-2")
            ])
        )
    
    return items


@callback(
    Output('performance-chart', 'figure'),
    Input('experiment-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_performance_chart(experiment_id, n):
    """Update experiment performance chart"""
    # Generate sample data
    metrics = ['Conversion Rate', 'Revenue per User', 'Session Duration']
    control = [0.12, 25.50, 8.5]
    treatment = [0.15, 28.75, 9.2]
    
    # Calculate lifts
    lifts = [(t - c) / c * 100 for c, t in zip(control, treatment)]
    
    fig = go.Figure()
    
    # Add control bars
    fig.add_trace(go.Bar(
        name='Control',
        x=metrics,
        y=control,
        marker_color=COLORS['text_secondary'],
        text=[f'{v:.2f}' for v in control],
        textposition='auto',
    ))
    
    # Add treatment bars
    fig.add_trace(go.Bar(
        name='Treatment',
        x=metrics,
        y=treatment,
        marker_color=COLORS['primary'],
        text=[f'{v:.2f}' for v in treatment],
        textposition='auto',
    ))
    
    fig.update_layout(
        barmode='group',
        title='Metric Comparison: Control vs Treatment',
        xaxis_title='Metrics',
        yaxis_title='Value',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


@callback(
    Output('significance-chart', 'figure'),
    Input('experiment-selector', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_significance_chart(experiment_id, n):
    """Update statistical significance chart"""
    # Generate sample data
    metrics = ['Conversion Rate', 'Revenue per User', 'Session Duration', 'Bounce Rate']
    p_values = [0.002, 0.015, 0.045, 0.120]
    lifts = [25.0, 12.7, 8.2, -5.3]
    
    # Determine significance
    colors = [COLORS['success'] if p < 0.05 else COLORS['text_secondary'] for p in p_values]
    
    fig = go.Figure()
    
    # Add bars for lift
    fig.add_trace(go.Bar(
        x=metrics,
        y=lifts,
        marker_color=colors,
        text=[f'{l:+.1f}%' for l in lifts],
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>Lift: %{y:.1f}%<br>p-value: %{customdata:.4f}<extra></extra>',
        customdata=p_values
    ))
    
    # Add significance threshold line
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    
    fig.update_layout(
        title='Relative Lift by Metric (with Statistical Significance)',
        xaxis_title='Metrics',
        yaxis_title='Relative Lift (%)',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


@callback(
    Output('experiments-table', 'children'),
    Input('url', 'pathname')
)
def update_experiments_table(pathname):
    """Update experiments table"""
    if pathname != '/experiments':
        return []
    
    experiments_data = [
        {
            'name': 'Homepage Redesign',
            'status': 'Active',
            'start_date': '2025-01-15',
            'users': '45,234',
            'conversion_lift': '+25.0%',
            'p_value': '0.002',
            'significant': 'Yes'
        },
        {
            'name': 'Checkout Flow',
            'status': 'Active',
            'start_date': '2025-01-20',
            'users': '32,156',
            'conversion_lift': '+8.5%',
            'p_value': '0.089',
            'significant': 'No'
        },
        {
            'name': 'Search Algorithm',
            'status': 'Active',
            'start_date': '2025-01-25',
            'users': '18,923',
            'conversion_lift': '+12.3%',
            'p_value': '0.034',
            'significant': 'Yes'
        },
    ]
    
    df = pd.DataFrame(experiments_data)
    
    table = dbc.Table.from_dataframe(
        df,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True,
        className="mb-0"
    )
    
    return table


@callback(
    Output('experiment-details', 'children'),
    Input('analysis-experiment-selector', 'value')
)
def update_experiment_details(experiment_id):
    """Update experiment details panel"""
    details = {
        'homepage_redesign_v1': {
            'name': 'Homepage Redesign',
            'status': 'Active',
            'start_date': '2025-01-15',
            'end_date': '2025-02-15',
            'variants': ['Control', 'Treatment'],
            'traffic': '50% / 50%',
            'users': '45,234'
        },
        'checkout_flow_v2': {
            'name': 'Checkout Flow',
            'status': 'Active',
            'start_date': '2025-01-20',
            'end_date': '2025-02-20',
            'variants': ['Control', 'Treatment A', 'Treatment B'],
            'traffic': '40% / 30% / 30%',
            'users': '32,156'
        }
    }
    
    exp = details.get(experiment_id, {})
    
    return html.Div([
        html.H6("Experiment Details", className="mb-3"),
        html.P([html.Strong("Status: "), exp.get('status', 'N/A')]),
        html.P([html.Strong("Start Date: "), exp.get('start_date', 'N/A')]),
        html.P([html.Strong("End Date: "), exp.get('end_date', 'N/A')]),
        html.P([html.Strong("Variants: "), ', '.join(exp.get('variants', []))]),
        html.P([html.Strong("Traffic Split: "), exp.get('traffic', 'N/A')]),
        html.P([html.Strong("Total Users: "), exp.get('users', 'N/A')]),
    ])


@callback(
    Output('analysis-content', 'children'),
    Input('analysis-tabs', 'active_tab'),
    Input('analysis-experiment-selector', 'value')
)
def update_analysis_content(active_tab, experiment_id):
    """Update analysis content based on selected tab"""
    if active_tab == 'metrics-tab':
        return create_metrics_tab_content(experiment_id)
    elif active_tab == 'stats-tab':
        return create_stats_tab_content(experiment_id)
    elif active_tab == 'timeseries-tab':
        return create_timeseries_tab_content(experiment_id)
    elif active_tab == 'guardrails-tab':
        return create_guardrails_tab_content(experiment_id)
    
    return html.Div("Select a tab")


def create_metrics_tab_content(experiment_id):
    """Create metrics tab content"""
    # Sample metrics data
    metrics_data = pd.DataFrame({
        'Metric': ['Conversion Rate', 'Revenue per User', 'Session Duration', 'Bounce Rate'],
        'Control': [0.12, 25.50, 8.5, 0.35],
        'Treatment': [0.15, 28.75, 9.2, 0.32],
        'Absolute Lift': [0.03, 3.25, 0.7, -0.03],
        'Relative Lift (%)': [25.0, 12.7, 8.2, -8.6],
        'P-Value': [0.002, 0.015, 0.045, 0.120],
        'Significant': ['✓', '✓', '✓', '✗']
    })
    
    table = dbc.Table.from_dataframe(
        metrics_data,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Metrics Summary", className="mb-3"),
            table
        ])
    ], className="shadow-sm")


def create_stats_tab_content(experiment_id):
    """Create statistical tests tab content"""
    # Create confidence interval visualization
    metrics = ['Conversion Rate', 'Revenue per User', 'Session Duration']
    lifts = [25.0, 12.7, 8.2]
    ci_lower = [15.2, 5.3, 2.1]
    ci_upper = [34.8, 20.1, 14.3]
    
    fig = go.Figure()
    
    for i, metric in enumerate(metrics):
        fig.add_trace(go.Scatter(
            x=[ci_lower[i], lifts[i], ci_upper[i]],
            y=[metric, metric, metric],
            mode='lines+markers',
            name=metric,
            line=dict(width=2),
            marker=dict(size=[8, 12, 8])
        ))
    
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    fig.update_layout(
        title='95% Confidence Intervals for Relative Lift',
        xaxis_title='Relative Lift (%)',
        yaxis_title='',
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Statistical Analysis", className="mb-3"),
            dcc.Graph(figure=fig),
            html.Hr(),
            html.H6("Test Details", className="mb-2"),
            html.P("Test Type: Bootstrap (10,000 iterations)"),
            html.P("Significance Level: α = 0.05"),
            html.P("Multiple Testing Correction: Benjamini-Hochberg"),
        ])
    ], className="shadow-sm")


def create_timeseries_tab_content(experiment_id):
    """Create time series tab content"""
    # Generate sample time series data
    dates = pd.date_range(start='2025-01-15', periods=30, freq='D')
    
    control_conversion = 0.12 + np.random.normal(0, 0.01, 30)
    treatment_conversion = 0.15 + np.random.normal(0, 0.01, 30)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=control_conversion,
        mode='lines+markers',
        name='Control',
        line=dict(color=COLORS['text_secondary'], width=2),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=dates,
        y=treatment_conversion,
        mode='lines+markers',
        name='Treatment',
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title='Conversion Rate Over Time',
        xaxis_title='Date',
        yaxis_title='Conversion Rate',
        template='plotly_white',
        height=400,
        hovermode='x unified'
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Time Series Analysis", className="mb-3"),
            dcc.Graph(figure=fig)
        ])
    ], className="shadow-sm")


def create_guardrails_tab_content(experiment_id):
    """Create guardrails tab content"""
    guardrails_data = pd.DataFrame({
        'Metric': ['Page Load Time', 'Error Rate', 'API Latency', 'Memory Usage'],
        'Control': [550, 0.5, 120, 256],
        'Treatment': [580, 0.6, 125, 260],
        'Change (%)': [5.5, 20.0, 4.2, 1.6],
        'Threshold (%)': [10.0, 5.0, 15.0, 20.0],
        'Status': ['✓ Pass', '✗ Fail', '✓ Pass', '✓ Pass']
    })
    
    table = dbc.Table.from_dataframe(
        guardrails_data,
        striped=True,
        bordered=True,
        hover=True,
        responsive=True
    )
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Guardrail Metrics", className="mb-3"),
            dbc.Alert(
                "⚠️ Warning: Error Rate has exceeded the guardrail threshold. Consider pausing the experiment.",
                color="warning",
                className="mb-3"
            ),
            table
        ])
    ], className="shadow-sm")


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
