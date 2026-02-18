import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional, Dict, Any
import re


def detect_chart_type(df: pd.DataFrame, query: str) -> Optional[str]:
    """
    Detect what type of chart would be appropriate based on the query and data.
    Returns: 'bar', 'line', 'pie', 'scatter', or None
    """
    query_lower = query.lower()
    
    # Trend/time-series patterns
    if any(word in query_lower for word in ['trend', 'over time', 'by month', 'by quarter', 'by year', 'timeline']):
        return 'line'
    
    # Comparison patterns
    if any(word in query_lower for word in ['compare', 'by category', 'by department', 'top', 'bottom', 'highest', 'lowest']):
        return 'bar'
    
    # Distribution patterns
    if any(word in query_lower for word in ['distribution', 'breakdown', 'composition', 'percentage', 'proportion']):
        return 'pie'
    
    # Correlation patterns
    if any(word in query_lower for word in ['correlation', 'relationship', 'vs', 'versus', 'against']):
        return 'scatter'
    
    return None


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create a beautiful bar chart"""
    fig = px.bar(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        color=y_col,
        color_continuous_scale='Blues',
        template='plotly_white'
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        showlegend=False,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    fig.update_traces(
        texttemplate='%{y:,.0f}',
        textposition='outside'
    )
    
    return fig


def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create a trend line chart"""
    fig = px.line(
        df,
        x=x_col,
        y=y_col,
        title=title,
        markers=True,
        template='plotly_white'
    )
    
    fig.update_traces(
        line_color='#1f77b4',
        marker=dict(size=8),
        line=dict(width=3)
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str = "") -> go.Figure:
    """Create a pie chart for distribution"""
    fig = px.pie(
        df,
        names=names_col,
        values=values_col,
        title=title,
        template='plotly_white'
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percent: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def create_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "") -> go.Figure:
    """Create a scatter plot for correlation"""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=title,
        trendline="ols",
        template='plotly_white'
    )
    
    fig.update_traces(
        marker=dict(size=10, color='#1f77b4', opacity=0.6)
    )
    
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        height=400,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    return fig


def parse_ai_response_for_data(response: str) -> Optional[pd.DataFrame]:
    """
    Try to extract structured data from AI response.
    Looks for patterns like "Label: Value" or table structures.
    """
    lines = response.split('\n')
    data_points = []
    
    # Pattern 1: "Label: Value" format
    for line in lines:
        line = line.strip()
        if ':' in line and '|' not in line:  # Avoid table separators
            parts = line.split(':', 1)
            if len(parts) == 2:
                label = parts[0].strip().lstrip('-•*').strip()
                value_str = parts[1].strip()
                
                # Extract numeric value
                numbers = re.findall(r'[\d,]+\.?\d*', value_str)
                if numbers and label:
                    try:
                        value = float(numbers[0].replace(',', ''))
                        data_points.append({'label': label, 'value': value})
                    except:
                        pass
    
    # Pattern 2: Markdown table
    if not data_points:
        table_lines = [l for l in lines if '|' in l]
        if len(table_lines) >= 3:  # Header + separator + at least 1 data row
            try:
                # Parse markdown table
                headers = [h.strip() for h in table_lines[0].split('|') if h.strip()]
                data_rows = []
                for line in table_lines[2:]:  # Skip header and separator
                    cells = [c.strip() for c in line.split('|') if c.strip()]
                    if cells:
                        data_rows.append(cells)
                
                if headers and data_rows:
                    df = pd.DataFrame(data_rows, columns=headers[:len(data_rows[0])])
                    # Try to convert numeric columns
                    for col in df.columns:
                        try:
                            df[col] = pd.to_numeric(df[col].str.replace(',', ''))
                        except:
                            pass
                    return df
            except:
                pass
    
    if len(data_points) >= 2:
        return pd.DataFrame(data_points)
    
    return None


def auto_visualize(df: pd.DataFrame, query: str, ai_response: str) -> Optional[go.Figure]:
    """
    Automatically generate a chart if the query warrants visualization.
    
    Args:
        df: Original CSV dataframe
        query: User's question
        ai_response: AI's text response
    
    Returns:
        Plotly figure or None
    """
    # First check if visualization would help
    chart_type = detect_chart_type(df, query)
    
    if not chart_type:
        return None
    
    # Try to extract data from AI response
    viz_df = parse_ai_response_for_data(ai_response)
    
    if viz_df is None or len(viz_df) < 2:
        return None
    
    # Generate appropriate chart
    title = query[:60] + "..." if len(query) > 60 else query
    
    try:
        if chart_type == 'bar':
            return create_bar_chart(viz_df, viz_df.columns[0], viz_df.columns[1], title)
        elif chart_type == 'line':
            return create_line_chart(viz_df, viz_df.columns[0], viz_df.columns[1], title)
        elif chart_type == 'pie':
            return create_pie_chart(viz_df, viz_df.columns[0], viz_df.columns[1], title)
        elif chart_type == 'scatter' and len(viz_df.columns) >= 2:
            return create_scatter_chart(viz_df, viz_df.columns[0], viz_df.columns[1], title)
    except Exception as e:
        print(f"Visualization error: {e}")
        return None
    
    return None