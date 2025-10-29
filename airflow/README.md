# Airflow DAGs for Experimentation Platform

This directory contains Apache Airflow DAGs for automating the experimentation pipeline.

## DAGs Overview

### 1. experiment_pipeline (Daily)
**Schedule:** Daily at 2 AM  
**Purpose:** Main data pipeline for experiment analysis

**Tasks:**
1. Extract experiment data from source database
2. Compute metrics for all active experiments
3. Run statistical tests (t-test, bootstrap, chi-square)
4. Check guardrail metrics for violations
5. Generate daily report
6. Update results database
7. Send email notifications

### 2. experiment_monitoring (Real-time)
**Schedule:** Every 15 minutes  
**Purpose:** Real-time monitoring for critical issues

**Tasks:**
1. Health check for running experiments
2. Detect critical issues (sample size, data quality, metric degradation)
3. Send immediate alerts if issues detected

### 3. experiment_cleanup (Weekly)
**Schedule:** Weekly on Sunday at 3 AM  
**Purpose:** Archive completed experiments and cleanup

**Tasks:**
1. Identify completed experiments
2. Archive data to cold storage
3. Clean up temporary data older than 30 days
4. Generate summary report

## Setup

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- PostgreSQL (for Airflow metadata)

### Installation

1. **Build and start Airflow:**
\`\`\`bash
cd airflow
docker-compose up -d
\`\`\`

2. **Access Airflow UI:**
- URL: http://localhost:8080
- Username: airflow
- Password: airflow

3. **Enable DAGs:**
- Navigate to the Airflow UI
- Toggle the DAGs to "On" state

### Configuration

Update `config/experiment_config.yaml` with your settings:
- Database connections
- Email recipients
- Statistical parameters
- Experiment definitions

## Monitoring

### Airflow UI
- View DAG runs and task status
- Check logs for debugging
- Monitor task duration and success rates

### Email Alerts
- Daily summary reports
- Critical issue alerts (real-time)
- Guardrail violation notifications

## Development

### Adding New DAGs
1. Create new DAG file in `airflow/dags/`
2. Import required modules from `src/ab_framework/`
3. Define tasks and dependencies
4. Test locally before deploying

### Testing DAGs
\`\`\`bash
# Test DAG structure
airflow dags test experiment_pipeline 2025-01-01

# Test specific task
airflow tasks test experiment_pipeline extract_experiment_data 2025-01-01
\`\`\`

## Troubleshooting

### Common Issues

**DAG not appearing:**
- Check DAG file for syntax errors
- Verify file is in `dags/` directory
- Check Airflow logs: `docker-compose logs airflow-scheduler`

**Task failures:**
- Check task logs in Airflow UI
- Verify database connections
- Ensure required data is available

**Email not sending:**
- Configure SMTP settings in `airflow.cfg`
- Check email addresses in DAG definitions

## Production Deployment

### Recommendations
1. Use managed Airflow service (Cloud Composer, MWAA, Astronomer)
2. Configure proper authentication and RBAC
3. Set up monitoring and alerting
4. Use secrets manager for credentials
5. Enable DAG versioning with Git
6. Configure appropriate resource limits
7. Set up backup and disaster recovery

### Environment Variables
\`\`\`bash
# Database connection
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://user:pass@host/db

# Email configuration
AIRFLOW__SMTP__SMTP_HOST=smtp.gmail.com
AIRFLOW__SMTP__SMTP_USER=your-email@gmail.com
AIRFLOW__SMTP__SMTP_PASSWORD=your-password
AIRFLOW__SMTP__SMTP_MAIL_FROM=your-email@gmail.com
