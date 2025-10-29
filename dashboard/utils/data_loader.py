"""
Data loading utilities for the dashboard.
Connects to data sources and prepares data for visualization.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ab_framework.metrics import MetricRegistry, MetricComputer
from src.ab_framework.stats_tests import ABTestAnalyzer


class ExperimentDataLoader:
    """
    Loads and prepares experiment data for dashboard visualization.
    """
    
    def __init__(self, data_source: str = "database"):
        """
        Initialize data loader.
        
        Args:
            data_source: Source of data ('database', 'file', 'api')
        """
        self.data_source = data_source
        self.metric_registry = MetricRegistry()
        self.metric_computer = MetricComputer(self.metric_registry)
        self.analyzer = ABTestAnalyzer()
    
    def load_experiment_data(
        self,
        experiment_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> pd.DataFrame:
        """
        Load raw experiment data.
        
        Args:
            experiment_id: Unique experiment identifier
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with experiment data
        """
        # TODO: Replace with actual database query
        # Example:
        # query = """
        #     SELECT * FROM experiment_events
        #     WHERE experiment_id = %s
        #     AND timestamp BETWEEN %s AND %s
        # """
        # return pd.read_sql(query, conn, params=[experiment_id, start_date, end_date])
        
        # For demo, generate sample data
        n_samples = 10000
        
        data = pd.DataFrame({
            'user_id': [f'user_{i}' for i in range(n_samples)],
            'experiment_id': [experiment_id] * n_samples,
            'variant': np.random.choice(['control', 'treatment'], n_samples),
            'converted': np.random.binomial(1, 0.13, n_samples),
            'revenue': np.random.exponential(25, n_samples),
            'session_duration_min': np.random.gamma(2, 4, n_samples),
            'timestamp': pd.date_range(
                start=start_date or datetime.now() - timedelta(days=30),
                periods=n_samples,
                freq='1min'
            )
        })
        
        return data
    
    def get_experiment_summary(self, experiment_id: str) -> Dict:
        """
        Get summary statistics for an experiment.
        
        Args:
            experiment_id: Unique experiment identifier
            
        Returns:
            Dictionary with summary statistics
        """
        data = self.load_experiment_data(experiment_id)
        
        summary = {
            'total_users': len(data),
            'start_date': data['timestamp'].min(),
            'end_date': data['timestamp'].max(),
            'variants': data['variant'].unique().tolist(),
            'variant_distribution': data['variant'].value_counts().to_dict()
        }
        
        return summary
    
    def get_metrics_by_variant(
        self,
        experiment_id: str
    ) -> pd.DataFrame:
        """
        Compute metrics for each variant.
        
        Args:
            experiment_id: Unique experiment identifier
            
        Returns:
            DataFrame with metrics by variant
        """
        data = self.load_experiment_data(experiment_id)
        
        metrics_df = self.metric_computer.compute_experiment_metrics(
            data,
            variant_column='variant'
        )
        
        return metrics_df
    
    def get_time_series_data(
        self,
        experiment_id: str,
        metric: str,
        frequency: str = 'D'
    ) -> pd.DataFrame:
        """
        Get time series data for a metric.
        
        Args:
            experiment_id: Unique experiment identifier
            metric: Metric to analyze
            frequency: Time frequency ('D', 'H', 'W')
            
        Returns:
            DataFrame with time series data
        """
        data = self.load_experiment_data(experiment_id)
        
        # Group by date and variant
        time_series = data.groupby([
            pd.Grouper(key='timestamp', freq=frequency),
            'variant'
        ])[metric].mean().reset_index()
        
        return time_series
    
    def get_statistical_results(
        self,
        experiment_id: str
    ) -> List[Dict]:
        """
        Get statistical test results for all metrics.
        
        Args:
            experiment_id: Unique experiment identifier
            
        Returns:
            List of test results
        """
        data = self.load_experiment_data(experiment_id)
        
        control_data = data[data['variant'] == 'control']
        treatment_data = data[data['variant'] == 'treatment']
        
        results = []
        
        metrics_to_test = ['revenue', 'session_duration_min']
        
        for metric in metrics_to_test:
            if metric not in data.columns:
                continue
            
            result = self.analyzer.bootstrap_test(
                control_data[metric].values,
                treatment_data[metric].values,
                metric_name=metric
            )
            
            results.append(result.to_dict())
        
        return results
    
    def check_data_quality(
        self,
        experiment_id: str
    ) -> Dict:
        """
        Check data quality for an experiment.
        
        Args:
            experiment_id: Unique experiment identifier
            
        Returns:
            Dictionary with data quality metrics
        """
        data = self.load_experiment_data(experiment_id)
        
        quality_metrics = {
            'total_records': len(data),
            'missing_values': data.isnull().sum().to_dict(),
            'duplicate_users': data['user_id'].duplicated().sum(),
            'variant_balance': data['variant'].value_counts(normalize=True).to_dict(),
            'date_range': {
                'start': data['timestamp'].min(),
                'end': data['timestamp'].max(),
                'days': (data['timestamp'].max() - data['timestamp'].min()).days
            }
        }
        
        return quality_metrics
