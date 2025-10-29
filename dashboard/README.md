# Experimentation Platform Dashboard

Interactive Plotly Dash dashboard for visualizing and analyzing A/B test experiments.

## Features

### 📊 Main Dashboard
- Real-time experiment monitoring
- Key performance indicators (KPIs)
- Active experiment list with progress tracking
- Recent activity feed
- Performance comparison charts
- Statistical significance visualization

### 🧪 Experiment Management
- View all experiments (active, completed, paused)
- Experiment details and configuration
- User allocation and traffic split
- Status tracking

### 📈 Detailed Analysis
- **Metrics Tab**: Comprehensive metric comparison
- **Statistical Tests Tab**: Confidence intervals and test results
- **Time Series Tab**: Metric evolution over time
- **Guardrails Tab**: Monitor critical metrics

### 🎨 Visualizations
- Bar charts for metric comparison
- Line charts for time series analysis
- Funnel charts for conversion analysis
- Distribution plots for data exploration
- Heatmaps for multi-dimensional analysis
- Sequential testing charts

## Installation

### Prerequisites
- Python 3.11+
- pip

### Install Dependencies

\`\`\`bash
pip install -r requirements.txt
\`\`\`

Required packages:
- dash
- dash-bootstrap-components
- plotly
- pandas
- numpy
- scipy

## Running the Dashboard

### Development Mode

\`\`\`bash
cd dashboard
python app.py
\`\`\`

The dashboard will be available at: **http://localhost:8050**

### Production Mode

For production deployment, use a WSGI server like Gunicorn:

\`\`\`bash
gunicorn app:server -b 0.0.0.0:8050 --workers 4
\`\`\`

## Configuration

### Environment Variables

\`\`\`bash
# Database connection
DATABASE_URL=postgresql://user:password@host:port/database

# Dashboard settings
DASH_DEBUG=False
DASH_HOST=0.0.0.0
DASH_PORT=8050

# Refresh interval (seconds)
REFRESH_INTERVAL=30
\`\`\`

### Color Scheme

Customize colors in `app.py`:

\`\`\`python
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72',
    'success': '#06A77D',
    'warning': '#F18F01',
    'danger': '#C73E1D',
}
\`\`\`

## Dashboard Structure

\`\`\`
dashboard/
├── app.py                  # Main application
├── components/
│   └── charts.py          # Reusable chart components
├── utils/
│   └── data_loader.py     # Data loading utilities
└── assets/                # Static assets (CSS, images)
\`\`\`

## Usage Guide

### Viewing Experiments

1. Navigate to the **Dashboard** page for an overview
2. Click on an experiment in the list to see details
3. Use the **Experiments** page to view all experiments in a table

### Analyzing Results

1. Go to the **Analysis** page
2. Select an experiment from the dropdown
3. Switch between tabs to view different analyses:
   - **Metrics**: Summary table with all metrics
   - **Statistical Tests**: Confidence intervals and significance
   - **Time Series**: Metric evolution over time
   - **Guardrails**: Monitor critical metrics

### Interpreting Charts

**Performance Chart:**
- Compares control vs treatment for key metrics
- Bars show absolute values
- Green indicates treatment is winning

**Significance Chart:**
- Shows relative lift percentage
- Green bars = statistically significant (p < 0.05)
- Gray bars = not significant

**Time Series:**
- Track metric evolution over time
- Detect trends and anomalies
- Hover for exact values

## Customization

### Adding New Charts

Create new chart functions in `components/charts.py`:

\`\`\`python
def create_custom_chart(data):
    fig = go.Figure()
    # Add your chart logic
    return fig
\`\`\`

### Adding New Pages

Add new routes in `app.py`:

\`\`\`python
@callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if pathname == '/custom-page':
        return create_custom_layout()
    # ...
\`\`\`

### Connecting to Real Data

Update `utils/data_loader.py` to connect to your database:

\`\`\`python
def load_experiment_data(self, experiment_id):
    import psycopg2
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    query = "SELECT * FROM experiments WHERE id = %s"
    return pd.read_sql(query, conn, params=[experiment_id])
\`\`\`

## Performance Optimization

### Caching

Use Dash caching for expensive computations:

\`\`\`python
from flask_caching import Cache

cache = Cache(app.server, config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': os.environ.get('REDIS_URL')
})

@cache.memoize(timeout=300)
def expensive_computation(experiment_id):
    # Your computation
    pass
\`\`\`

### Data Sampling

For large datasets, implement sampling:

\`\`\`python
def load_experiment_data(self, experiment_id, sample_size=10000):
    query = """
        SELECT * FROM experiments
        WHERE id = %s
        ORDER BY RANDOM()
        LIMIT %s
    """
    return pd.read_sql(query, conn, params=[experiment_id, sample_size])
\`\`\`

## Troubleshooting

### Dashboard not loading
- Check if port 8050 is available
- Verify all dependencies are installed
- Check console for error messages

### Charts not updating
- Verify callback functions are defined correctly
- Check data source connections
- Inspect browser console for JavaScript errors

### Slow performance
- Implement caching
- Reduce refresh interval
- Optimize database queries
- Use data sampling for large datasets

## Deployment

### Docker

\`\`\`dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app:server", "-b", "0.0.0.0:8050", "--workers", "4"]
\`\`\`

### Kubernetes

See `k8s/` directory for Kubernetes deployment manifests.

## Support

For issues or questions:
- Check the documentation
- Review error logs
- Contact the data team

## License

Internal use only - Company Confidential
