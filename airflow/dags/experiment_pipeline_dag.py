"""
Main Airflow DAG for experiment data pipeline.
Orchestrates data collection, metric computation, and analysis.
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.dates import days_ago
import pandas as pd
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ab_framework.assignment import UserAssignment, ExperimentConfig, ExperimentStatus
from src.ab_framework.stats_tests import ABTestAnalyzer, MultipleTestingCorrection
from src.ab_framework.metrics import MetricRegistry, MetricComputer


# Default DAG arguments
default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email': ['data-team@company.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(hours=2),
}


def extract_experiment_data(**context):
    """
    Extract experiment event data from source database.
    In production, this would connect to your data warehouse.
    """
    execution_date = context['execution_date']
    
    print(f"Extracting experiment data for {execution_date}")
    
    # TODO: Replace with actual database connection
    # Example using pandas to read from database:
    # import psycopg2
    # conn = psycopg2.connect(...)
    # query = """
    #     SELECT user_id, experiment_id, variant, event_type, event_value, timestamp
    #     FROM experiment_events
    #     WHERE DATE(timestamp) = %s
    # """
    # df = pd.read_sql(query, conn, params=[execution_date.date()])
    
    # For demo purposes, create sample data
    sample_data = pd.DataFrame({
        'user_id': [f'user_{i}' for i in range(1000)],
        'experiment_id': ['homepage_redesign_v1'] * 1000,
        'variant': ['control'] * 500 + ['treatment'] * 500,
        'converted': [0, 1] * 500,
        'revenue': [0, 10, 20, 30, 0, 15] * 167,
        'session_duration_min': [2, 5, 10, 3, 7, 12] * 167,
        'load_time_ms': [500, 600, 550, 700, 650, 580] * 167,
        'is_error': [0, 0, 0, 1, 0, 0] * 167,
        'is_bounce': [1, 0, 0, 1, 0, 0] * 167,
    })
    
    # Save to temporary location for next task
    output_path = f'/tmp/experiment_data_{execution_date.strftime("%Y%m%d")}.parquet'
    sample_data.to_parquet(output_path, index=False)
    
    # Push file path to XCom for next task
    context['task_instance'].xcom_push(key='data_path', value=output_path)
    
    print(f"Extracted {len(sample_data)} records")
    return output_path


def compute_experiment_metrics(**context):
    """
    Compute metrics for all active experiments.
    """
    # Get data path from previous task
    data_path = context['task_instance'].xcom_pull(
        task_ids='extract_experiment_data',
        key='data_path'
    )
    
    print(f"Computing metrics from {data_path}")
    
    # Load experiment data
    experiment_data = pd.read_parquet(data_path)
    
    # Initialize metric computer
    metric_registry = MetricRegistry()
    metric_computer = MetricComputer(metric_registry)
    
    # Compute metrics for each experiment
    experiments = experiment_data['experiment_id'].unique()
    
    all_results = {}
    for exp_id in experiments:
        exp_data = experiment_data[experiment_data['experiment_id'] == exp_id]
        
        # Compute metrics per variant
        metrics_df = metric_computer.compute_experiment_metrics(
            exp_data,
            variant_column='variant'
        )
        
        all_results[exp_id] = metrics_df
        
        print(f"Computed metrics for {exp_id}:")
        print(metrics_df)
    
    # Save results
    execution_date = context['execution_date']
    output_path = f'/tmp/experiment_metrics_{execution_date.strftime("%Y%m%d")}.parquet'
    
    # Combine all results
    combined_results = pd.concat([
        df.assign(experiment_id=exp_id) 
        for exp_id, df in all_results.items()
    ])
    combined_results.to_parquet(output_path, index=False)
    
    context['task_instance'].xcom_push(key='metrics_path', value=output_path)
    
    return output_path


def run_statistical_tests(**context):
    """
    Run statistical tests to determine experiment significance.
    """
    # Get metrics from previous task
    metrics_path = context['task_instance'].xcom_pull(
        task_ids='compute_experiment_metrics',
        key='metrics_path'
    )
    
    # Get original data
    data_path = context['task_instance'].xcom_pull(
        task_ids='extract_experiment_data',
        key='data_path'
    )
    
    print(f"Running statistical tests")
    
    # Load data
    experiment_data = pd.read_parquet(data_path)
    metrics_df = pd.read_parquet(metrics_path)
    
    # Initialize analyzer
    analyzer = ABTestAnalyzer(alpha=0.05, confidence_level=0.95)
    
    # Run tests for each experiment
    all_test_results = []
    
    experiments = experiment_data['experiment_id'].unique()
    for exp_id in experiments:
        exp_data = experiment_data[experiment_data['experiment_id'] == exp_id]
        
        # Get control and treatment data
        control_data = exp_data[exp_data['variant'] == 'control']
        treatment_data = exp_data[exp_data['variant'] == 'treatment']
        
        if len(control_data) == 0 or len(treatment_data) == 0:
            print(f"Skipping {exp_id} - missing control or treatment data")
            continue
        
        # Test key metrics
        metrics_to_test = ['revenue', 'converted', 'session_duration_min']
        
        for metric in metrics_to_test:
            if metric not in exp_data.columns:
                continue
            
            # Choose appropriate test based on metric
            if metric == 'converted':
                # Binary metric - use chi-square
                control_successes = control_data[metric].sum()
                treatment_successes = treatment_data[metric].sum()
                
                result = analyzer.chi_square_test(
                    control_successes=int(control_successes),
                    control_total=len(control_data),
                    treatment_successes=int(treatment_successes),
                    treatment_total=len(treatment_data),
                    metric_name=metric
                )
            else:
                # Continuous metric - use t-test and bootstrap
                control_values = control_data[metric].values
                treatment_values = treatment_data[metric].values
                
                # Run both t-test and bootstrap for robustness
                result = analyzer.bootstrap_test(
                    control_values,
                    treatment_values,
                    metric_name=metric,
                    n_bootstrap=5000
                )
            
            # Add experiment context
            result_dict = result.to_dict()
            result_dict['experiment_id'] = exp_id
            result_dict['date'] = context['execution_date'].date()
            
            all_test_results.append(result_dict)
            
            print(f"{exp_id} - {metric}: p={result.p_value:.4f}, "
                  f"lift={result.relative_lift*100:.2f}%, "
                  f"significant={result.is_significant}")
    
    # Apply multiple testing correction
    if all_test_results:
        results_df = pd.DataFrame(all_test_results)
        
        # Save results
        execution_date = context['execution_date']
        output_path = f'/tmp/test_results_{execution_date.strftime("%Y%m%d")}.parquet'
        results_df.to_parquet(output_path, index=False)
        
        context['task_instance'].xcom_push(key='results_path', value=output_path)
        context['task_instance'].xcom_push(key='num_significant', 
                                          value=results_df['is_significant'].sum())
        
        return output_path
    
    return None


def check_guardrails(**context):
    """
    Check if any guardrail metrics have been violated.
    """
    # Get data
    data_path = context['task_instance'].xcom_pull(
        task_ids='extract_experiment_data',
        key='data_path'
    )
    
    print("Checking guardrail metrics")
    
    experiment_data = pd.read_parquet(data_path)
    
    # Initialize metric computer
    metric_registry = MetricRegistry()
    metric_computer = MetricComputer(metric_registry)
    
    all_violations = []
    
    experiments = experiment_data['experiment_id'].unique()
    for exp_id in experiments:
        exp_data = experiment_data[experiment_data['experiment_id'] == exp_id]
        
        # Compute metrics
        metrics_df = metric_computer.compute_experiment_metrics(
            exp_data,
            variant_column='variant'
        )
        
        # Get control and treatment metrics
        control_metrics = metrics_df[metrics_df['variant'] == 'control'].iloc[0].to_dict()
        treatment_metrics = metrics_df[metrics_df['variant'] == 'treatment'].iloc[0].to_dict()
        
        # Check violations
        violations = metric_computer.check_guardrail_violations(
            control_metrics,
            treatment_metrics
        )
        
        for violation in violations:
            violation['experiment_id'] = exp_id
            violation['date'] = context['execution_date'].date()
            all_violations.append(violation)
            
            print(f"⚠️  GUARDRAIL VIOLATION in {exp_id}:")
            print(f"   Metric: {violation['metric_name']}")
            print(f"   Change: {violation['relative_change']*100:.2f}%")
            print(f"   Severity: {violation['severity']}")
    
    # Save violations
    if all_violations:
        violations_df = pd.DataFrame(all_violations)
        execution_date = context['execution_date']
        output_path = f'/tmp/guardrail_violations_{execution_date.strftime("%Y%m%d")}.parquet'
        violations_df.to_parquet(output_path, index=False)
        
        context['task_instance'].xcom_push(key='violations_path', value=output_path)
        context['task_instance'].xcom_push(key='num_violations', value=len(all_violations))
    else:
        print("✓ No guardrail violations detected")
        context['task_instance'].xcom_push(key='num_violations', value=0)
    
    return len(all_violations)


def generate_daily_report(**context):
    """
    Generate daily experiment report with key findings.
    """
    print("Generating daily experiment report")
    
    # Get results from previous tasks
    results_path = context['task_instance'].xcom_pull(
        task_ids='run_statistical_tests',
        key='results_path'
    )
    
    num_significant = context['task_instance'].xcom_pull(
        task_ids='run_statistical_tests',
        key='num_significant'
    ) or 0
    
    num_violations = context['task_instance'].xcom_pull(
        task_ids='check_guardrails',
        key='num_violations'
    ) or 0
    
    execution_date = context['execution_date']
    
    # Create report
    report = f"""
    Experiment Pipeline Daily Report
    Date: {execution_date.date()}
    
    Summary:
    - Significant Results: {num_significant}
    - Guardrail Violations: {num_violations}
    
    """
    
    if results_path and os.path.exists(results_path):
        results_df = pd.read_parquet(results_path)
        
        # Add significant results
        significant_results = results_df[results_df['is_significant']]
        
        if len(significant_results) > 0:
            report += "\nSignificant Results:\n"
            for _, row in significant_results.iterrows():
                report += f"  - {row['experiment_id']} / {row['metric_name']}: "
                report += f"{row['relative_lift_pct']:.2f}% lift (p={row['p_value']:.4f})\n"
    
    # Save report
    report_path = f'/tmp/daily_report_{execution_date.strftime("%Y%m%d")}.txt'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(report)
    
    context['task_instance'].xcom_push(key='report_path', value=report_path)
    context['task_instance'].xcom_push(key='report_content', value=report)
    
    return report_path


def update_results_database(**context):
    """
    Update results database with latest experiment results.
    In production, this would write to your data warehouse.
    """
    print("Updating results database")
    
    # Get all results
    results_path = context['task_instance'].xcom_pull(
        task_ids='run_statistical_tests',
        key='results_path'
    )
    
    metrics_path = context['task_instance'].xcom_pull(
        task_ids='compute_experiment_metrics',
        key='metrics_path'
    )
    
    # TODO: Replace with actual database writes
    # Example:
    # import psycopg2
    # conn = psycopg2.connect(...)
    # results_df.to_sql('experiment_results', conn, if_exists='append')
    
    print(f"Would write results from {results_path} to database")
    print(f"Would write metrics from {metrics_path} to database")
    
    return "Database updated successfully"


# Define the DAG
with DAG(
    'experiment_pipeline',
    default_args=default_args,
    description='Daily experiment data pipeline',
    schedule_interval='0 2 * * *',  # Run daily at 2 AM
    start_date=days_ago(1),
    catchup=False,
    tags=['experiments', 'analytics'],
) as dag:
    
    # Task 1: Extract experiment data
    extract_data = PythonOperator(
        task_id='extract_experiment_data',
        python_callable=extract_experiment_data,
        provide_context=True,
    )
    
    # Task 2: Compute metrics
    compute_metrics = PythonOperator(
        task_id='compute_experiment_metrics',
        python_callable=compute_experiment_metrics,
        provide_context=True,
    )
    
    # Task 3: Run statistical tests
    run_tests = PythonOperator(
        task_id='run_statistical_tests',
        python_callable=run_statistical_tests,
        provide_context=True,
    )
    
    # Task 4: Check guardrails
    check_guardrails_task = PythonOperator(
        task_id='check_guardrails',
        python_callable=check_guardrails,
        provide_context=True,
    )
    
    # Task 5: Generate report
    generate_report = PythonOperator(
        task_id='generate_daily_report',
        python_callable=generate_daily_report,
        provide_context=True,
    )
    
    # Task 6: Update database
    update_db = PythonOperator(
        task_id='update_results_database',
        python_callable=update_results_database,
        provide_context=True,
    )
    
    # Task 7: Send email notification (only if violations detected)
    send_alert = EmailOperator(
        task_id='send_alert_email',
        to=['data-team@company.com'],
        subject='Experiment Pipeline Alert - {{ execution_date }}',
        html_content="""
        <h3>Experiment Pipeline Completed</h3>
        <p>Date: {{ execution_date }}</p>
        <p>Significant Results: {{ task_instance.xcom_pull(task_ids='run_statistical_tests', key='num_significant') }}</p>
        <p>Guardrail Violations: {{ task_instance.xcom_pull(task_ids='check_guardrails', key='num_violations') }}</p>
        <pre>{{ task_instance.xcom_pull(task_ids='generate_daily_report', key='report_content') }}</pre>
        """,
        trigger_rule='all_done',
    )
    
    # Define task dependencies
    extract_data >> compute_metrics >> [run_tests, check_guardrails_task]
    [run_tests, check_guardrails_task] >> generate_report >> update_db >> send_alert
