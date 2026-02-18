import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict, Any
import numpy as np


def generate_kpi_cards(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Generate key metrics/KPI cards for the dashboard"""
    cards = []
    
    # Total rows
    cards.append({
        'title': 'Total Records',
        'value': f"{len(df):,}",
        'icon': '📊',
        'delta': None
    })
    
    # Total columns
    cards.append({
        'title': 'Total Columns',
        'value': f"{len(df.columns)}",
        'icon': '📋',
        'delta': None
    })
    
    # Numeric columns analysis
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        cards.append({
            'title': 'Numeric Fields',
            'value': f"{len(numeric_cols)}",
            'icon': '🔢',
            'delta': None
        })
    
    # Missing values
    missing_total = df.isnull().sum().sum()
    missing_pct = (missing_total / (len(df) * len(df.columns)) * 100)
    cards.append({
        'title': 'Missing Values',
        'value': f"{missing_total:,}",
        'icon': '⚠️',
        'delta': f"{missing_pct:.1f}%"
    })
    
    return cards


def create_column_distribution_chart(df: pd.DataFrame) -> go.Figure:
    """Create a chart showing data type distribution"""
    dtype_counts = df.dtypes.value_counts()
    
    fig = px.pie(
        values=dtype_counts.values,
        names=[str(dt) for dt in dtype_counts.index],
        title="Column Data Types Distribution",
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True
    )
    
    return fig


def create_missing_values_chart(df: pd.DataFrame) -> go.Figure:
    """Create a chart showing missing values per column"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    
    # Only show columns with missing values
    missing_data = pd.DataFrame({
        'Column': missing[missing > 0].index,
        'Count': missing[missing > 0].values,
        'Percentage': missing_pct[missing > 0].values
    })
    
    if len(missing_data) == 0:
        # No missing values - create empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="✅ No Missing Values Detected",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="green")
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    fig = px.bar(
        missing_data,
        x='Column',
        y='Percentage',
        title="Missing Values by Column (%)",
        color='Percentage',
        color_continuous_scale='Reds',
        text='Percentage'
    )
    
    fig.update_traces(
        texttemplate='%{text:.1f}%',
        textposition='outside'
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        xaxis_title="Column",
        yaxis_title="Missing %"
    )
    
    return fig


def create_numeric_summary_chart(df: pd.DataFrame) -> go.Figure:
    """Create box plots for numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No Numeric Columns Found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Limit to first 5 numeric columns for readability
    cols_to_plot = numeric_cols[:5]
    
    fig = go.Figure()
    
    for col in cols_to_plot:
        fig.add_trace(go.Box(
            y=df[col].dropna(),
            name=col,
            boxmean='sd'
        ))
    
    fig.update_layout(
        title="Numeric Columns Distribution",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        yaxis_title="Value"
    )
    
    return fig


def create_categorical_chart(df: pd.DataFrame) -> go.Figure:
    """Create a chart showing top categories in categorical columns"""
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(categorical_cols) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="No Categorical Columns Found",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Pick first categorical column with reasonable unique values
    selected_col = None
    for col in categorical_cols:
        unique_count = df[col].nunique()
        if 2 <= unique_count <= 20:  # Sweet spot for visualization
            selected_col = col
            break
    
    if selected_col is None and len(categorical_cols) > 0:
        selected_col = categorical_cols[0]
    
    value_counts = df[selected_col].value_counts().head(10)
    
    fig = px.bar(
        x=value_counts.index,
        y=value_counts.values,
        title=f"Top Values in '{selected_col}'",
        labels={'x': selected_col, 'y': 'Count'},
        color=value_counts.values,
        color_continuous_scale='Blues'
    )
    
    fig.update_traces(
        texttemplate='%{y:,}',
        textposition='outside'
    )
    
    fig.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
        xaxis_title=selected_col,
        yaxis_title="Count"
    )
    
    return fig


def create_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Create correlation heatmap for numeric columns"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    if len(numeric_cols) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Need at least 2 numeric columns for correlation",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Limit to first 6 numeric columns
    cols_to_use = numeric_cols[:6]
    corr_matrix = df[cols_to_use].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="Correlation Heatmap",
        height=350,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    
    return fig


def generate_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Generate summary statistics table"""
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) == 0:
        return pd.DataFrame({
            'Message': ['No numeric columns in dataset']
        })
    
    stats = numeric_df.describe().T
    stats['missing'] = df[numeric_df.columns].isnull().sum()
    stats['missing_pct'] = (stats['missing'] / len(df) * 100).round(2)
    
    # Reorder columns
    stats = stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max', 'missing', 'missing_pct']]
    
    # Round for display
    stats = stats.round(2)
    
    return stats