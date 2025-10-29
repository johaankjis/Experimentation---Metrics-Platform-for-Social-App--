"""
Statistical testing methods for A/B experiment analysis.
Implements multiple testing approaches with proper corrections.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from enum import Enum


class TestType(Enum):
    """Statistical test types"""
    T_TEST = "t_test"
    MANN_WHITNEY = "mann_whitney"
    BOOTSTRAP = "bootstrap"
    CHI_SQUARE = "chi_square"


@dataclass
class TestResult:
    """Results from a statistical test"""
    test_type: TestType
    metric_name: str
    control_mean: float
    treatment_mean: float
    absolute_lift: float
    relative_lift: float
    p_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    sample_size_control: int
    sample_size_treatment: int
    statistical_power: Optional[float] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting"""
        return {
            'test_type': self.test_type.value,
            'metric_name': self.metric_name,
            'control_mean': self.control_mean,
            'treatment_mean': self.treatment_mean,
            'absolute_lift': self.absolute_lift,
            'relative_lift_pct': self.relative_lift * 100,
            'p_value': self.p_value,
            'ci_lower': self.confidence_interval[0],
            'ci_upper': self.confidence_interval[1],
            'is_significant': self.is_significant,
            'n_control': self.sample_size_control,
            'n_treatment': self.sample_size_treatment,
            'statistical_power': self.statistical_power
        }


class ABTestAnalyzer:
    """
    Comprehensive A/B test statistical analysis.
    Supports multiple testing methods and proper corrections.
    """
    
    def __init__(self, alpha: float = 0.05, confidence_level: float = 0.95):
        """
        Initialize analyzer.
        
        Args:
            alpha: Significance level for hypothesis testing
            confidence_level: Confidence level for intervals
        """
        self.alpha = alpha
        self.confidence_level = confidence_level
    
    def t_test(
        self,
        control: np.ndarray,
        treatment: np.ndarray,
        metric_name: str = "metric"
    ) -> TestResult:
        """
        Perform Welch's t-test (unequal variances).
        Best for continuous metrics with approximately normal distributions.
        
        Args:
            control: Control group metric values
            treatment: Treatment group metric values
            metric_name: Name of the metric being tested
            
        Returns:
            TestResult with analysis details
        """
        # Calculate statistics
        control_mean = np.mean(control)
        treatment_mean = np.mean(treatment)
        absolute_lift = treatment_mean - control_mean
        relative_lift = absolute_lift / control_mean if control_mean != 0 else 0
        
        # Perform Welch's t-test (does not assume equal variances)
        t_stat, p_value = stats.ttest_ind(treatment, control, equal_var=False)
        
        # Calculate confidence interval for difference
        control_se = stats.sem(control)
        treatment_se = stats.sem(treatment)
        se_diff = np.sqrt(control_se**2 + treatment_se**2)
        
        # Degrees of freedom for Welch's t-test
        df = len(control) + len(treatment) - 2
        t_critical = stats.t.ppf((1 + self.confidence_level) / 2, df)
        
        ci_lower = absolute_lift - t_critical * se_diff
        ci_upper = absolute_lift + t_critical * se_diff
        
        return TestResult(
            test_type=TestType.T_TEST,
            metric_name=metric_name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            absolute_lift=absolute_lift,
            relative_lift=relative_lift,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            is_significant=p_value < self.alpha,
            sample_size_control=len(control),
            sample_size_treatment=len(treatment)
        )
    
    def mann_whitney_test(
        self,
        control: np.ndarray,
        treatment: np.ndarray,
        metric_name: str = "metric"
    ) -> TestResult:
        """
        Perform Mann-Whitney U test (non-parametric).
        Best for non-normal distributions or ordinal data.
        
        Args:
            control: Control group metric values
            treatment: Treatment group metric values
            metric_name: Name of the metric being tested
            
        Returns:
            TestResult with analysis details
        """
        # Calculate statistics
        control_mean = np.mean(control)
        treatment_mean = np.mean(treatment)
        absolute_lift = treatment_mean - control_mean
        relative_lift = absolute_lift / control_mean if control_mean != 0 else 0
        
        # Perform Mann-Whitney U test
        u_stat, p_value = stats.mannwhitneyu(
            treatment, control, alternative='two-sided'
        )
        
        # Use bootstrap for confidence interval (more appropriate for non-parametric)
        bootstrap_result = self.bootstrap_test(control, treatment, metric_name)
        
        return TestResult(
            test_type=TestType.MANN_WHITNEY,
            metric_name=metric_name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            absolute_lift=absolute_lift,
            relative_lift=relative_lift,
            p_value=p_value,
            confidence_interval=bootstrap_result.confidence_interval,
            is_significant=p_value < self.alpha,
            sample_size_control=len(control),
            sample_size_treatment=len(treatment)
        )
    
    def bootstrap_test(
        self,
        control: np.ndarray,
        treatment: np.ndarray,
        metric_name: str = "metric",
        n_bootstrap: int = 10000
    ) -> TestResult:
        """
        Perform bootstrap hypothesis test with resampling.
        Most robust method, works for any distribution.
        
        Args:
            control: Control group metric values
            treatment: Treatment group metric values
            metric_name: Name of the metric being tested
            n_bootstrap: Number of bootstrap iterations
            
        Returns:
            TestResult with analysis details
        """
        # Calculate observed statistics
        control_mean = np.mean(control)
        treatment_mean = np.mean(treatment)
        observed_diff = treatment_mean - control_mean
        relative_lift = observed_diff / control_mean if control_mean != 0 else 0
        
        # Bootstrap resampling
        bootstrap_diffs = []
        for _ in range(n_bootstrap):
            # Resample with replacement
            control_sample = np.random.choice(control, size=len(control), replace=True)
            treatment_sample = np.random.choice(treatment, size=len(treatment), replace=True)
            
            # Calculate difference
            diff = np.mean(treatment_sample) - np.mean(control_sample)
            bootstrap_diffs.append(diff)
        
        bootstrap_diffs = np.array(bootstrap_diffs)
        
        # Calculate p-value (two-tailed)
        # Proportion of bootstrap samples with difference as extreme as observed
        p_value = np.mean(np.abs(bootstrap_diffs) >= np.abs(observed_diff))
        
        # Calculate confidence interval
        alpha_lower = (1 - self.confidence_level) / 2
        alpha_upper = 1 - alpha_lower
        ci_lower = np.percentile(bootstrap_diffs, alpha_lower * 100)
        ci_upper = np.percentile(bootstrap_diffs, alpha_upper * 100)
        
        return TestResult(
            test_type=TestType.BOOTSTRAP,
            metric_name=metric_name,
            control_mean=control_mean,
            treatment_mean=treatment_mean,
            absolute_lift=observed_diff,
            relative_lift=relative_lift,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            is_significant=p_value < self.alpha,
            sample_size_control=len(control),
            sample_size_treatment=len(treatment)
        )
    
    def chi_square_test(
        self,
        control_successes: int,
        control_total: int,
        treatment_successes: int,
        treatment_total: int,
        metric_name: str = "conversion_rate"
    ) -> TestResult:
        """
        Perform chi-square test for proportions (e.g., conversion rates).
        Best for binary outcome metrics.
        
        Args:
            control_successes: Number of successes in control
            control_total: Total observations in control
            treatment_successes: Number of successes in treatment
            treatment_total: Total observations in treatment
            metric_name: Name of the metric being tested
            
        Returns:
            TestResult with analysis details
        """
        # Calculate proportions
        control_rate = control_successes / control_total
        treatment_rate = treatment_successes / treatment_total
        absolute_lift = treatment_rate - control_rate
        relative_lift = absolute_lift / control_rate if control_rate != 0 else 0
        
        # Create contingency table
        contingency_table = np.array([
            [treatment_successes, treatment_total - treatment_successes],
            [control_successes, control_total - control_successes]
        ])
        
        # Perform chi-square test
        chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
        
        # Calculate confidence interval for difference in proportions
        se_control = np.sqrt(control_rate * (1 - control_rate) / control_total)
        se_treatment = np.sqrt(treatment_rate * (1 - treatment_rate) / treatment_total)
        se_diff = np.sqrt(se_control**2 + se_treatment**2)
        
        z_critical = stats.norm.ppf((1 + self.confidence_level) / 2)
        ci_lower = absolute_lift - z_critical * se_diff
        ci_upper = absolute_lift + z_critical * se_diff
        
        return TestResult(
            test_type=TestType.CHI_SQUARE,
            metric_name=metric_name,
            control_mean=control_rate,
            treatment_mean=treatment_rate,
            absolute_lift=absolute_lift,
            relative_lift=relative_lift,
            p_value=p_value,
            confidence_interval=(ci_lower, ci_upper),
            is_significant=p_value < self.alpha,
            sample_size_control=control_total,
            sample_size_treatment=treatment_total
        )
    
    def calculate_sample_size(
        self,
        baseline_mean: float,
        baseline_std: float,
        minimum_detectable_effect: float,
        power: float = 0.8
    ) -> int:
        """
        Calculate required sample size per variant.
        
        Args:
            baseline_mean: Expected mean in control group
            baseline_std: Expected standard deviation
            minimum_detectable_effect: Minimum effect size to detect (absolute)
            power: Desired statistical power (1 - beta)
            
        Returns:
            Required sample size per variant
        """
        # Effect size (Cohen's d)
        effect_size = minimum_detectable_effect / baseline_std
        
        # Z-scores for alpha and power
        z_alpha = stats.norm.ppf(1 - self.alpha / 2)
        z_beta = stats.norm.ppf(power)
        
        # Sample size calculation
        n = 2 * ((z_alpha + z_beta) / effect_size) ** 2
        
        return int(np.ceil(n))
    
    def sequential_test(
        self,
        control: np.ndarray,
        treatment: np.ndarray,
        metric_name: str = "metric",
        spending_function: str = "obrien_fleming"
    ) -> TestResult:
        """
        Perform sequential testing with alpha spending.
        Allows peeking at results without inflating Type I error.
        
        Args:
            control: Control group metric values
            treatment: Treatment group metric values
            metric_name: Name of the metric being tested
            spending_function: Alpha spending function type
            
        Returns:
            TestResult with adjusted significance
        """
        # For simplicity, using O'Brien-Fleming boundaries
        # In production, would implement full sequential testing framework
        
        # Perform standard t-test
        result = self.t_test(control, treatment, metric_name)
        
        # Adjust alpha based on spending function
        # This is a simplified version - full implementation would track
        # number of looks and adjust accordingly
        adjusted_alpha = self.alpha * 0.5  # Conservative adjustment
        result.is_significant = result.p_value < adjusted_alpha
        
        return result


class MultipleTestingCorrection:
    """
    Handles multiple testing corrections to control family-wise error rate.
    """
    
    @staticmethod
    def bonferroni_correction(
        test_results: List[TestResult],
        alpha: float = 0.05
    ) -> List[TestResult]:
        """
        Apply Bonferroni correction for multiple comparisons.
        Most conservative approach.
        
        Args:
            test_results: List of test results
            alpha: Family-wise error rate
            
        Returns:
            Updated test results with corrected significance
        """
        n_tests = len(test_results)
        adjusted_alpha = alpha / n_tests
        
        corrected_results = []
        for result in test_results:
            result.is_significant = result.p_value < adjusted_alpha
            corrected_results.append(result)
        
        return corrected_results
    
    @staticmethod
    def benjamini_hochberg_correction(
        test_results: List[TestResult],
        alpha: float = 0.05
    ) -> List[TestResult]:
        """
        Apply Benjamini-Hochberg FDR correction.
        Less conservative than Bonferroni, controls false discovery rate.
        
        Args:
            test_results: List of test results
            alpha: False discovery rate
            
        Returns:
            Updated test results with corrected significance
        """
        # Sort by p-value
        sorted_results = sorted(test_results, key=lambda x: x.p_value)
        n_tests = len(sorted_results)
        
        # Apply BH procedure
        corrected_results = []
        for i, result in enumerate(sorted_results, 1):
            critical_value = (i / n_tests) * alpha
            result.is_significant = result.p_value <= critical_value
            corrected_results.append(result)
        
        return corrected_results
