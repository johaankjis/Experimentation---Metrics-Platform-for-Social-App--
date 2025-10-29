"""
Real-time experiment monitoring DAG.
Runs more frequently to detect issues early.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ab_framework.stats_tests import ABTestAnalyzer
from src.ab_framework.metrics import MetricRegistry, MetricComputer


default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-team@company.com'],
    'email_on_failure': True,
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
}


def check_experiment_health(**context):
    """
    Quick health check for running experiments.
    Detects critical issues that need immediate attention.
    """
    print("Running experiment health check")
    
    # TODO: Connect to real-time data source
    # For demo, simulate health check
    
    issues = []
    
    # Check 1: Sample size adequacy
    # Check 2: Assignment balance
    # Check 3: Data quality
    # Check 4: Critical metric degradation
    
    # Simulate finding an issue
    has_critical_issue = False  # Set to True to test alerting
    
    if has_critical_issue:
        issues.append({
            'severity': 'critical',
            'experiment_id': 'homepage_redesign_v1',
            'issue': 'Conversion rate dropped by 50%',
            'recommendation': 'Consider pausing experiment'
        })
    
    context['task_instance'].xcom_push(key='has_issues', value=len(issues) > 0)
    context['task_instance'].xcom_push(key='issues', value=issues)
    
    return len(issues)


def decide_alert_path(**context):
    """
    Decide whether to send alert based on health check.
    """
    has_issues = context['task_instance'].xcom_pull(
        task_ids='check_experiment_health',
        key='has_issues'
    )
    
    if has_issues:
        return 'send_critical_alert'
    else:
        return 'log_healthy_status'


def log_healthy_status(**context):
    """
    Log that all experiments are healthy.
    """
    print("✓ All experiments healthy")
    return "healthy"


def send_critical_alert_content(**context):
    """
    Prepare critical alert content.
    """
    issues = context['task_instance'].xcom_pull(
        task_ids='check_experiment_health',
        key='issues'
    )
    
    alert_content = "<h2>🚨 Critical Experiment Issues Detected</h2>"
    
    for issue in issues:
        alert_content += f"""
        <div style="border: 2px solid red; padding: 10px; margin: 10px 0;">
            <h3>{issue['experiment_id']}</h3>
            <p><strong>Severity:</strong> {issue['severity']}</p>
            <p><strong>Issue:</strong> {issue['issue']}</p>
            <p><strong>Recommendation:</strong> {issue['recommendation']}</p>
        </div>
        """
    
    return alert_content


# Define monitoring DAG
with DAG(
    'experiment_monitoring',
    default_args=default_args,
    description='Real-time experiment monitoring',
    schedule_interval='*/15 * * * *',  # Run every 15 minutes
    start_date=days_ago(1),
    catchup=False,
    tags=['experiments', 'monitoring', 'real-time'],
) as dag:
    
    health_check = PythonOperator(
        task_id='check_experiment_health',
        python_callable=check_experiment_health,
        provide_context=True,
    )
    
    decide_alert = BranchPythonOperator(
        task_id='decide_alert_path',
        python_callable=decide_alert_path,
        provide_context=True,
    )
    
    log_healthy = PythonOperator(
        task_id='log_healthy_status',
        python_callable=log_healthy_status,
        provide_context=True,
    )
    
    send_alert = EmailOperator(
        task_id='send_critical_alert',
        to=['data-team@company.com', 'product-team@company.com'],
        subject='🚨 CRITICAL: Experiment Issue Detected',
        html_content="{{ task_instance.xcom_pull(task_ids='check_experiment_health', key='issues') }}",
    )
    
    health_check >> decide_alert >> [log_healthy, send_alert]
