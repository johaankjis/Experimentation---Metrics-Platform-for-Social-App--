# Experimentation & Metrics Platform for Social Apps

A comprehensive A/B testing and experimentation platform designed for social media applications. This platform enables data-driven product decisions through rigorous statistical testing, real-time monitoring, and intuitive dashboards.

## 🎯 Overview

This platform provides end-to-end capabilities for running and analyzing experiments:

- **Statistical Framework**: Python-based A/B testing framework with multiple statistical tests
- **Interactive Dashboards**: Next.js and Plotly Dash visualizations for experiment monitoring
- **Automated Pipelines**: Apache Airflow DAGs for data processing and experiment management
- **User Assignment**: Deterministic hash-based randomization for consistent user experiences
- **Metrics Governance**: Comprehensive metric definitions with guardrails and validations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│  ┌──────────────────────┐    ┌─────────────────────────┐   │
│  │  Next.js Dashboard   │    │  Plotly Dash Dashboard  │   │
│  │  (React/TypeScript)  │    │      (Python)           │   │
│  └──────────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   A/B Testing Framework                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Assignment  │  │   Metrics    │  │ Stats Tests  │     │
│  │    Logic     │  │  Computation │  │  (t-test,    │     │
│  │              │  │              │  │  bootstrap)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Pipeline (Airflow)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Experiment  │  │  Monitoring  │  │   Cleanup    │     │
│  │   Pipeline   │  │      DAG     │  │     DAG      │     │
│  │   (Daily)    │  │  (15 min)    │  │  (Weekly)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Storage                            │
│  ┌──────────────────────┐    ┌─────────────────────────┐   │
│  │  Analytics Database  │    │  Experiment Results DB  │   │
│  └──────────────────────┘    └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Repository Structure

```
.
├── src/ab_framework/          # Core Python A/B testing framework
│   ├── assignment.py          # User assignment and bucketing logic
│   ├── metrics.py             # Metric definitions and computations
│   └── stats_tests.py         # Statistical testing methods
│
├── app/                       # Next.js application
│   ├── layout.tsx             # Root layout
│   └── page.tsx               # Main page
│
├── components/                # React components
│   ├── experiment-dashboard.tsx
│   ├── statistical-chart.tsx
│   ├── metrics-catalog.tsx
│   └── ui/                    # Reusable UI components
│
├── dashboard/                 # Plotly Dash dashboard
│   ├── app.py                 # Main dashboard application
│   ├── components/            # Dashboard components
│   │   └── charts.py          # Chart components
│   └── utils/                 # Utilities
│       └── data_loader.py     # Data loading utilities
│
├── airflow/                   # Apache Airflow DAGs
│   ├── dags/
│   │   ├── experiment_pipeline_dag.py
│   │   ├── experiment_monitoring_dag.py
│   │   └── experiment_cleanup_dag.py
│   └── docker-compose.yml     # Airflow setup
│
├── config/                    # Configuration files
│   └── experiment_config.yaml # Experiment and metric definitions
│
└── public/                    # Static assets
```

## 🚀 Quick Start

### Prerequisites

- **Node.js** 22+ and pnpm
- **Python** 3.11+
- **Docker** and Docker Compose (for Airflow)
- **PostgreSQL** (optional, for production)

### 1. Install Frontend Dependencies

```bash
# Install Node.js dependencies
pnpm install
```

### 2. Run Next.js Dashboard

```bash
# Development mode
pnpm run dev

# Production build
pnpm run build
pnpm start
```

The Next.js dashboard will be available at: **http://localhost:3000**

### 3. Run Plotly Dash Dashboard

```bash
# Install Python dependencies
pip install -r dashboard/requirements.txt

# Run the dashboard
cd dashboard
python app.py
```

The Plotly dashboard will be available at: **http://localhost:8050**

### 4. Setup Airflow (Optional)

```bash
# Start Airflow services
cd airflow
docker-compose up -d

# Access Airflow UI at: http://localhost:8080
# Username: airflow
# Password: airflow
```

## 📊 Key Features

### 1. A/B Testing Framework

**User Assignment (`src/ab_framework/assignment.py`)**
- Deterministic hash-based randomization
- Consistent user experiences across sessions
- Support for multi-variant experiments
- Traffic allocation control

**Metrics System (`src/ab_framework/metrics.py`)**
- North-star metrics (primary success metrics)
- Guardrail metrics (metrics that shouldn't degrade)
- Diagnostic metrics (supporting metrics)
- Flexible metric definitions and computations

**Statistical Testing (`src/ab_framework/stats_tests.py`)**
- T-tests for continuous metrics
- Chi-square tests for categorical metrics
- Bootstrap methods for non-parametric testing
- Multiple testing corrections (Benjamini-Hochberg, Bonferroni)
- Confidence interval estimation
- Statistical power analysis

### 2. Interactive Dashboards

**Next.js Dashboard (Modern Web UI)**
- Real-time experiment monitoring
- Interactive charts and visualizations
- Responsive design with mobile support
- Built with React, TypeScript, and Tailwind CSS
- Shadcn/ui components for consistent design

**Plotly Dash Dashboard (Analytics Focus)**
- Comprehensive metric comparison
- Time series analysis
- Funnel charts and conversion analysis
- Distribution plots and heatmaps
- Statistical test results visualization

### 3. Automated Data Pipeline

**Experiment Pipeline DAG** (Daily at 2 AM)
- Extract experiment data
- Compute metrics for all active experiments
- Run statistical tests
- Check guardrail metrics
- Generate daily reports
- Send email notifications

**Monitoring DAG** (Every 15 minutes)
- Real-time health checks
- Detect critical issues
- Immediate alerts for problems
- Sample size monitoring

**Cleanup DAG** (Weekly on Sunday)
- Archive completed experiments
- Clean up old temporary data
- Generate summary reports

## 🔧 Configuration

### Experiment Configuration

Edit `config/experiment_config.yaml` to define experiments and metrics:

```yaml
experiments:
  - experiment_id: "homepage_redesign_v1"
    name: "Homepage Redesign Test"
    status: "active"
    variants:
      - name: "control"
        traffic_allocation: 0.5
      - name: "treatment"
        traffic_allocation: 0.5
    primary_metrics:
      - "conversion_rate"
      - "revenue_per_user"
    guardrail_metrics:
      - "page_load_time"
      - "error_rate"
```

### Statistical Settings

Configure statistical parameters in the config file:

```yaml
platform:
  statistical_settings:
    default_alpha: 0.05
    default_confidence_level: 0.95
    default_power: 0.80
    multiple_testing_correction: "benjamini_hochberg"
```

## 💻 Usage Examples

### Running an Experiment

```python
from src.ab_framework.assignment import UserAssignment, ExperimentConfig, ExperimentStatus

# Define experiment
experiment = ExperimentConfig(
    experiment_id="new_feature_test",
    name="New Feature Test",
    variants=["control", "treatment"],
    traffic_allocation={"control": 0.5, "treatment": 0.5},
    status=ExperimentStatus.ACTIVE
)

# Assign users
assigner = UserAssignment()
variant = assigner.assign_user(
    user_id="user_12345",
    experiment=experiment
)
print(f"User assigned to: {variant}")
```

### Computing Metrics

```python
from src.ab_framework.metrics import MetricDefinition, MetricType, MetricAggregation

# Define a metric
conversion_metric = MetricDefinition(
    metric_id="conversion_rate",
    name="Conversion Rate",
    description="Percentage of users who completed checkout",
    metric_type=MetricType.NORTH_STAR,
    aggregation=MetricAggregation.RATE,
    minimum_sample_size=1000,
    minimum_detectable_effect=0.02
)
```

### Running Statistical Tests

```python
from src.ab_framework.stats_tests import StatisticalTester, TestType

# Prepare data
control_data = [100, 105, 98, 102, 99, 103, 101]
treatment_data = [110, 115, 108, 112, 109, 113, 111]

# Run t-test
tester = StatisticalTester()
result = tester.t_test(
    control=control_data,
    treatment=treatment_data,
    metric_name="revenue_per_user",
    alpha=0.05
)

print(f"Relative Lift: {result.relative_lift * 100:.2f}%")
print(f"P-value: {result.p_value:.4f}")
print(f"Significant: {result.is_significant}")
```

## 📈 Dashboard Features

### Next.js Dashboard Pages

1. **Overview Dashboard**
   - Active experiments summary
   - Key performance indicators
   - Recent activity feed
   - Quick performance comparisons

2. **Experiment Catalog**
   - Browse all experiments
   - Filter by status (active, completed, paused)
   - View experiment configurations

3. **Statistical Analysis**
   - Detailed metric comparisons
   - Confidence intervals
   - Time series trends
   - Guardrail monitoring

### Plotly Dash Dashboard Tabs

1. **Metrics Tab**: Summary table with all metrics
2. **Statistical Tests Tab**: Confidence intervals and significance
3. **Time Series Tab**: Metric evolution over time
4. **Guardrails Tab**: Monitor critical metrics

## 🧪 Testing

### Running Frontend Tests

```bash
# Run linting
pnpm run lint

# Build to check for errors
pnpm run build
```

### Running Python Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest src/ab_framework/tests/

# Run with coverage
pytest --cov=src/ab_framework src/ab_framework/tests/
```

## 🛠️ Development

### Adding a New Metric

1. Define the metric in `config/experiment_config.yaml`
2. Add computation logic in `src/ab_framework/metrics.py`
3. Update dashboard to display the metric

### Creating a New Experiment

1. Define experiment in `config/experiment_config.yaml`
2. Configure variants and traffic allocation
3. Specify primary and guardrail metrics
4. Enable the experiment (status: "active")
5. Monitor in dashboards

### Adding a New Statistical Test

1. Implement test in `src/ab_framework/stats_tests.py`
2. Add test type to `TestType` enum
3. Update `StatisticalTester` class with new method
4. Document the test methodology

## 🔒 Security Considerations

- Use environment variables for sensitive credentials
- Never commit secrets to the repository
- Implement proper authentication for dashboards
- Use HTTPS in production
- Follow the principle of least privilege for database access
- Regularly update dependencies

## 📚 Additional Documentation

- [Dashboard Documentation](./dashboard/README.md) - Detailed Plotly Dash dashboard guide
- [Airflow Documentation](./airflow/README.md) - Airflow DAG setup and usage
- [Experiment Configuration](./config/experiment_config.yaml) - Configuration reference

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make your changes with clear commit messages
3. Add tests for new functionality
4. Run linting and tests
5. Submit a pull request

## 📝 Best Practices

### Experimentation

- **Define clear hypotheses** before running experiments
- **Set sample size requirements** based on minimum detectable effect
- **Monitor guardrail metrics** to ensure no degradation
- **Run experiments for sufficient duration** to account for weekly patterns
- **Apply multiple testing corrections** when testing multiple metrics
- **Document experiment learnings** for future reference

### Statistical Analysis

- **Check sample size adequacy** before drawing conclusions
- **Consider statistical power** when planning experiments
- **Use appropriate tests** for metric types (t-test for continuous, chi-square for categorical)
- **Report confidence intervals** along with p-values
- **Be cautious of p-hacking** and sequential testing without proper corrections

### Platform Usage

- **Use semantic versioning** for experiment IDs
- **Archive completed experiments** to keep the platform clean
- **Monitor data quality** regularly
- **Set up proper alerting** for critical issues
- **Document experiment configurations** thoroughly

## 📊 Metrics Glossary

### North-Star Metrics
Primary success metrics that directly measure business impact:
- **Conversion Rate**: Percentage of users completing desired action
- **Revenue Per User**: Average revenue generated per user
- **User Retention**: Percentage of users returning after initial visit

### Guardrail Metrics
Metrics that should not degrade during experiments:
- **Page Load Time**: Time to fully load page content
- **Error Rate**: Percentage of requests resulting in errors
- **App Crash Rate**: Frequency of application crashes

### Diagnostic Metrics
Supporting metrics for understanding user behavior:
- **Session Duration**: Average time users spend in session
- **Bounce Rate**: Percentage of single-page sessions
- **Click-Through Rate**: Percentage of users clicking on elements

## 🐛 Troubleshooting

### Frontend Issues

**Dashboard not loading**
- Check if Node.js and pnpm are installed correctly
- Run `pnpm install` to ensure dependencies are installed
- Check console for error messages
- Verify port 3000 is available

**Build errors**
- Clear `.next` directory: `rm -rf .next`
- Reinstall dependencies: `rm -rf node_modules && pnpm install`
- Check TypeScript errors: `pnpm run lint`

### Backend Issues

**Plotly dashboard not starting**
- Ensure Python 3.11+ is installed
- Install dependencies: `pip install -r dashboard/requirements.txt`
- Check port 8050 is available
- Verify data source connections

**Airflow DAGs not appearing**
- Check DAG file syntax: `python airflow/dags/experiment_pipeline_dag.py`
- Verify file is in correct directory
- Check Airflow logs: `docker-compose logs airflow-scheduler`
- Ensure DAG is not paused in UI

## 📞 Support

For issues, questions, or feature requests:
- Check existing documentation
- Review troubleshooting section
- Check error logs
- Contact the data engineering team

## 📄 License

Internal use only - Company Confidential

---

**Built with ❤️ for data-driven product development**
