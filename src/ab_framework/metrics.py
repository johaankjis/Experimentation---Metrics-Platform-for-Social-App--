"""
Metric definitions and governance for experimentation platform.
Defines north-star metrics, guardrails, and metric computation logic.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum


class MetricType(Enum):
    """Types of metrics in the platform"""
    NORTH_STAR = "north_star"  # Primary success metric
    GUARDRAIL = "guardrail"    # Metrics that should not degrade
    DIAGNOSTIC = "diagnostic"   # Supporting metrics for understanding
    COUNTER = "counter"         # Simple count metrics


class MetricAggregation(Enum):
    """Aggregation methods for metrics"""
    MEAN = "mean"
    MEDIAN = "median"
    SUM = "sum"
    COUNT = "count"
    RATE = "rate"
    PERCENTILE_95 = "p95"
    PERCENTILE_99 = "p99"


@dataclass
class MetricDefinition:
    """
    Definition of a metric for experimentation.
    Includes computation logic and governance rules.
    """
    metric_id: str
    name: str
    description: str
    metric_type: MetricType
    aggregation: MetricAggregation
    computation_function: Optional[Callable] = None
    
    # Governance rules
    minimum_sample_size: int = 100
    minimum_detectable_effect: Optional[float] = None
    guardrail_threshold: Optional[float] = None  # For guardrail metrics
    
    # Data source
    source_table: Optional[str] = None
    source_column: Optional[str] = None
    
    def compute(self, data: pd.DataFrame) -> float:
        """
        Compute metric value from data.
        
        Args:
            data: DataFrame with metric data
            
        Returns:
            Computed metric value
        """
        if self.computation_function:
            return self.computation_function(data)
        
        # Default computation based on aggregation type
        if self.source_column not in data.columns:
            raise ValueError(f"Column {self.source_column} not found in data")
        
        values = data[self.source_column].dropna()
        
        if self.aggregation == MetricAggregation.MEAN:
            return values.mean()
        elif self.aggregation == MetricAggregation.MEDIAN:
            return values.median()
        elif self.aggregation == MetricAggregation.SUM:
            return values.sum()
        elif self.aggregation == MetricAggregation.COUNT:
            return len(values)
        elif self.aggregation == MetricAggregation.PERCENTILE_95:
            return values.quantile(0.95)
        elif self.aggregation == MetricAggregation.PERCENTILE_99:
            return values.quantile(0.99)
        else:
            raise ValueError(f"Unsupported aggregation: {self.aggregation}")


class MetricRegistry:
    """
    Central registry for all platform metrics.
    Ensures consistent metric definitions across experiments.
    """
    
    def __init__(self):
        self.metrics: Dict[str, MetricDefinition] = {}
        self._initialize_default_metrics()
    
    def _initialize_default_metrics(self):
        """Initialize common metrics for the platform"""
        
        # North Star Metrics
        self.register_metric(MetricDefinition(
            metric_id="revenue_per_user",
            name="Revenue Per User",
            description="Average revenue generated per user",
            metric_type=MetricType.NORTH_STAR,
            aggregation=MetricAggregation.MEAN,
            source_column="revenue",
            minimum_sample_size=1000,
            minimum_detectable_effect=0.05  # 5% lift
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="conversion_rate",
            name="Conversion Rate",
            description="Percentage of users who complete target action",
            metric_type=MetricType.NORTH_STAR,
            aggregation=MetricAggregation.MEAN,
            source_column="converted",
            minimum_sample_size=500,
            minimum_detectable_effect=0.02  # 2 percentage points
        ))
        
        # Guardrail Metrics
        self.register_metric(MetricDefinition(
            metric_id="page_load_time",
            name="Page Load Time",
            description="Average page load time in seconds",
            metric_type=MetricType.GUARDRAIL,
            aggregation=MetricAggregation.MEDIAN,
            source_column="load_time_ms",
            minimum_sample_size=500,
            guardrail_threshold=0.1  # Don't increase by more than 10%
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="error_rate",
            name="Error Rate",
            description="Percentage of requests resulting in errors",
            metric_type=MetricType.GUARDRAIL,
            aggregation=MetricAggregation.MEAN,
            source_column="is_error",
            minimum_sample_size=1000,
            guardrail_threshold=0.05  # Don't increase by more than 5%
        ))
        
        # Diagnostic Metrics
        self.register_metric(MetricDefinition(
            metric_id="session_duration",
            name="Session Duration",
            description="Average time users spend in session (minutes)",
            metric_type=MetricType.DIAGNOSTIC,
            aggregation=MetricAggregation.MEAN,
            source_column="session_duration_min",
            minimum_sample_size=500
        ))
        
        self.register_metric(MetricDefinition(
            metric_id="bounce_rate",
            name="Bounce Rate",
            description="Percentage of single-page sessions",
            metric_type=MetricType.DIAGNOSTIC,
            aggregation=MetricAggregation.MEAN,
            source_column="is_bounce",
            minimum_sample_size=500
        ))
    
    def register_metric(self, metric: MetricDefinition):
        """
        Register a new metric in the registry.
        
        Args:
            metric: MetricDefinition to register
        """
        if metric.metric_id in self.metrics:
            raise ValueError(f"Metric {metric.metric_id} already registered")
        
        self.metrics[metric.metric_id] = metric
    
    def get_metric(self, metric_id: str) -> MetricDefinition:
        """
        Retrieve metric definition by ID.
        
        Args:
            metric_id: Unique metric identifier
            
        Returns:
            MetricDefinition
        """
        if metric_id not in self.metrics:
            raise ValueError(f"Metric {metric_id} not found in registry")
        
        return self.metrics[metric_id]
    
    def get_metrics_by_type(self, metric_type: MetricType) -> List[MetricDefinition]:
        """
        Get all metrics of a specific type.
        
        Args:
            metric_type: Type of metrics to retrieve
            
        Returns:
            List of MetricDefinitions
        """
        return [
            metric for metric in self.metrics.values()
            if metric.metric_type == metric_type
        ]
    
    def list_all_metrics(self) -> pd.DataFrame:
        """
        Get summary of all registered metrics.
        
        Returns:
            DataFrame with metric information
        """
        metrics_data = []
        for metric in self.metrics.values():
            metrics_data.append({
                'metric_id': metric.metric_id,
                'name': metric.name,
                'type': metric.metric_type.value,
                'aggregation': metric.aggregation.value,
                'min_sample_size': metric.minimum_sample_size,
                'mde': metric.minimum_detectable_effect,
                'guardrail_threshold': metric.guardrail_threshold
            })
        
        return pd.DataFrame(metrics_data)


class MetricComputer:
    """
    Computes metrics for experiment analysis.
    Handles data aggregation and metric calculation.
    """
    
    def __init__(self, metric_registry: MetricRegistry):
        self.registry = metric_registry
    
    def compute_experiment_metrics(
        self,
        experiment_data: pd.DataFrame,
        variant_column: str = 'variant',
        metrics_to_compute: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Compute all metrics for each variant in an experiment.
        
        Args:
            experiment_data: DataFrame with experiment data
            variant_column: Column name containing variant assignments
            metrics_to_compute: List of metric IDs to compute (None = all)
            
        Returns:
            DataFrame with computed metrics per variant
        """
        if metrics_to_compute is None:
            metrics_to_compute = list(self.registry.metrics.keys())
        
        results = []
        
        for variant in experiment_data[variant_column].unique():
            variant_data = experiment_data[experiment_data[variant_column] == variant]
            
            variant_metrics = {'variant': variant, 'sample_size': len(variant_data)}
            
            for metric_id in metrics_to_compute:
                try:
                    metric_def = self.registry.get_metric(metric_id)
                    value = metric_def.compute(variant_data)
                    variant_metrics[metric_id] = value
                except Exception as e:
                    print(f"Error computing {metric_id} for {variant}: {e}")
                    variant_metrics[metric_id] = None
            
            results.append(variant_metrics)
        
        return pd.DataFrame(results)
    
    def check_guardrail_violations(
        self,
        control_metrics: Dict[str, float],
        treatment_metrics: Dict[str, float]
    ) -> List[Dict]:
        """
        Check if any guardrail metrics have been violated.
        
        Args:
            control_metrics: Metric values for control group
            treatment_metrics: Metric values for treatment group
            
        Returns:
            List of guardrail violations
        """
        violations = []
        
        guardrail_metrics = self.registry.get_metrics_by_type(MetricType.GUARDRAIL)
        
        for metric in guardrail_metrics:
            if metric.metric_id not in control_metrics or metric.metric_id not in treatment_metrics:
                continue
            
            control_value = control_metrics[metric.metric_id]
            treatment_value = treatment_metrics[metric.metric_id]
            
            if control_value == 0:
                continue
            
            relative_change = (treatment_value - control_value) / control_value
            
            if metric.guardrail_threshold and abs(relative_change) > metric.guardrail_threshold:
                violations.append({
                    'metric_id': metric.metric_id,
                    'metric_name': metric.name,
                    'control_value': control_value,
                    'treatment_value': treatment_value,
                    'relative_change': relative_change,
                    'threshold': metric.guardrail_threshold,
                    'severity': 'high' if abs(relative_change) > metric.guardrail_threshold * 2 else 'medium'
                })
        
        return violations
    
    def validate_sample_sizes(
        self,
        experiment_data: pd.DataFrame,
        variant_column: str = 'variant',
        metrics_to_check: Optional[List[str]] = None
    ) -> Dict[str, bool]:
        """
        Validate that sample sizes meet minimum requirements.
        
        Args:
            experiment_data: DataFrame with experiment data
            variant_column: Column name containing variant assignments
            metrics_to_check: List of metric IDs to validate
            
        Returns:
            Dictionary mapping metric_id to validation status
        """
        if metrics_to_check is None:
            metrics_to_check = list(self.registry.metrics.keys())
        
        validation_results = {}
        
        for metric_id in metrics_to_check:
            metric_def = self.registry.get_metric(metric_id)
            
            # Check sample size for each variant
            min_variant_size = experiment_data[variant_column].value_counts().min()
            
            validation_results[metric_id] = min_variant_size >= metric_def.minimum_sample_size
        
        return validation_results
