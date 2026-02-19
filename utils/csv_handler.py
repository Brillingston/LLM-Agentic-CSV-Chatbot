import pandas as pd


def load_csv(uploaded_file) -> pd.DataFrame:
    """Load CSV file from Streamlit uploader into a DataFrame."""
    try:
        df = pd.read_csv(uploaded_file)
        return df
    except Exception as e:
        raise ValueError(f"Error loading CSV: {str(e)}")


def get_csv_summary(df: pd.DataFrame) -> dict:
    """Return a summary dictionary of the DataFrame."""
    summary = {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "columns": list(df.columns),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "sample_data": df.head(5).to_dict(orient="records"),
        "null_counts": df.isnull().sum().to_dict(),
    }
    return summary


def dataframe_to_string(df: pd.DataFrame, max_rows: int = 50) -> str:
    """
    Convert DataFrame to a readable string for the LLM context.
    Uses intelligent sampling to show data variety within token limits.
    IMPORTANT: Reduced to 50 rows max to prevent token limit errors.
    """
    if len(df) <= max_rows:
        # Small dataset - show all
        return df.to_string(index=False)
    
    # Large dataset - smart sampling
    sample_size = max_rows // 2
    
    # Take first few rows
    head_df = df.head(sample_size)
    
    # Take last few rows  
    tail_df = df.tail(sample_size)
    
    # Combine with separator
    result = head_df.to_string(index=False)
    result += f"\n\n... [{len(df) - max_rows} rows omitted for brevity] ...\n\n"
    result += tail_df.to_string(index=False)
    
    return result


def get_column_info(df: pd.DataFrame) -> str:
    """Get detailed column information as a string."""
    info_lines = []
    for col in df.columns:
        dtype = df[col].dtype
        non_null = df[col].count()
        unique = df[col].nunique()

        if dtype in ["int64", "float64"]:
            info_lines.append(
                f"- {col} ({dtype}): {non_null} non-null, {unique} unique, "
                f"min={df[col].min()}, max={df[col].max()}, mean={df[col].mean():.2f}"
            )
        else:
            # Limit sample values to 3 to save tokens
            sample_vals = df[col].dropna().unique()[:3].tolist()
            info_lines.append(
                f"- {col} ({dtype}): {non_null} non-null, {unique} unique, "
                f"sample: {sample_vals}"
            )

    return "\n".join(info_lines)