"""
Reusable chart components for the dashboard.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import List, Dict, Optional


class ExperimentCharts:
    """Factory class for creating experiment visualization charts"""
    
    def __init__(self, color_scheme: Optional[Dict[str, str]] = None):
        self.colors = color_scheme or {
            'primary': '#2E86AB',
            'secondary': '#A23B72',
            'success': '#06A77D',
            'warning': '#F18F01',
            'danger': '#C73E1D',
        }
    
    def create_funnel_chart(
        self,
        stages: List[str],
        control_values: List[float],
        treatment_values: List[float]
    ) -> go.Figure:
        """
        Create a funnel chart comparing control and treatment.
        
        Args:
            stages: List of funnel stage names
            control_values: Values for control group
            treatment_values: Values for treatment group
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Funnel(
            name='Control',
            y=stages,
            x=control_values,
            textinfo="value+percent initial",
            marker=dict(color=self.colors['secondary'])
        ))
        
        fig.add_trace(go.Funnel(
            name='Treatment',
            y=stages,
            x=treatment_values,
            textinfo="value+percent initial",
            marker=dict(color=self.colors['primary'])
        ))
        
        fig.update_layout(
            title='Conversion Funnel Comparison',
            template='plotly_white',
            height=500
        )
        
        return fig
    
    def create_distribution_chart(
        self,
        control_data: np.ndarray,
        treatment_data: np.ndarray,
        metric_name: str
    ) -> go.Figure:
        """
        Create overlapping distribution charts.
        
        Args:
            control_data: Control group data
            treatment_data: Treatment group data
            metric_name: Name of the metric
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=control_data,
            name='Control',
            opacity=0.6,
            marker_color=self.colors['secondary'],
            nbinsx=30
        ))
        
        fig.add_trace(go.Histogram(
            x=treatment_data,
            name='Treatment',
            opacity=0.6,
            marker_color=self.colors['primary'],
            nbinsx=30
        ))
        
        fig.update_layout(
            title=f'Distribution of {metric_name}',
            xaxis_title=metric_name,
            yaxis_title='Frequency',
            barmode='overlay',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_sequential_testing_chart(
        self,
        dates: List[str],
        p_values: List[float],
        alpha: float = 0.05
    ) -> go.Figure:
        """
        Create sequential testing chart showing p-value evolution.
        
        Args:
            dates: List of dates
            p_values: P-values over time
            alpha: Significance threshold
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        # Add p-value line
        fig.add_trace(go.Scatter(
            x=dates,
            y=p_values,
            mode='lines+markers',
            name='P-Value',
            line=dict(color=self.colors['primary'], width=2),
            marker=dict(size=8)
        ))
        
        # Add significance threshold
        fig.add_hline(
            y=alpha,
            line_dash="dash",
            line_color=self.colors['danger'],
            annotation_text=f"α = {alpha}",
            annotation_position="right"
        )
        
        fig.update_layout(
            title='Sequential Testing: P-Value Over Time',
            xaxis_title='Date',
            yaxis_title='P-Value',
            template='plotly_white',
            height=400,
            yaxis_type='log'
        )
        
        return fig
    
    def create_sample_size_chart(
        self,
        dates: List[str],
        control_sizes: List[int],
        treatment_sizes: List[int]
    ) -> go.Figure:
        """
        Create sample size evolution chart.
        
        Args:
            dates: List of dates
            control_sizes: Control group sample sizes
            treatment_sizes: Treatment group sample sizes
            
        Returns:
            Plotly figure
        """
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=control_sizes,
            mode='lines',
            name='Control',
            fill='tozeroy',
            line=dict(color=self.colors['secondary'], width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=dates,
            y=treatment_sizes,
            mode='lines',
            name='Treatment',
            fill='tozeroy',
            line=dict(color=self.colors['primary'], width=2)
        ))
        
        fig.update_layout(
            title='Sample Size Growth',
            xaxis_title='Date',
            yaxis_title='Number of Users',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    def create_heatmap(
        self,
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        value_col: str
    ) -> go.Figure:
        """
        Create a heatmap for metric analysis.
        
        Args:
            data: DataFrame with data
            x_col: Column for x-axis
            y_col: Column for y-axis
            value_col: Column for values
            
        Returns:
            Plotly figure
        """
        pivot_data = data.pivot(index=y_col, columns=x_col, values=value_col)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_data.values,
            x=pivot_data.columns,
            y=pivot_data.index,
            colorscale='RdYlGn',
            text=pivot_data.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Metric Heatmap',
            template='plotly_white',
            height=500
        )
        
        return fig
