# backend/core/data_context.py
import pandas as pd
import numpy as np

def generate_data_context(df):
    """
    Generate a comprehensive data context for the LLM to understand the dataset.
    This function provides raw data insights without making assumptions about content.
    
    Args:
        df (pd.DataFrame): The dataset to analyze
        
    Returns:
        str: Formatted context string describing the dataset
    """
    if df is None or df.empty:
        return "No data available."
    
    context_parts = []
    
    # Basic dataset information
    context_parts.append(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Column information with data types and sample values
    context_parts.append("\nColumns and Data Types:")
    for col in df.columns[:20]:  # Show more columns since we removed hardcoding
        dtype = str(df[col].dtype)
        null_count = df[col].isnull().sum()
        null_pct = (null_count / len(df) * 100) if len(df) > 0 else 0
        
        if df[col].dtype in ['object', 'category', 'string']:
            unique_count = df[col].nunique()
            if unique_count <= 10 and unique_count > 0:
                # Show actual unique values for small categorical sets
                unique_values = df[col].dropna().unique()[:5]
                sample_values = f" (values: {', '.join(map(str, unique_values))})"
                if unique_count > 5:
                    sample_values += f" ...+{unique_count-5} more"
            else:
                sample_values = f" ({unique_count} unique values)"
            context_parts.append(f"- {col}: {dtype}{sample_values} | {null_pct:.1f}% null")
            
        elif df[col].dtype in ['datetime64[ns]', 'datetime64', 'datetime']:
            # Handle datetime columns
            try:
                min_date = df[col].min()
                max_date = df[col].max()
                context_parts.append(f"- {col}: {dtype} | Range: {min_date} to {max_date} | {null_pct:.1f}% null")
            except:
                context_parts.append(f"- {col}: {dtype} | {null_pct:.1f}% null")
                
        else:
            # Numeric columns
            try:
                if not df[col].isnull().all():
                    min_val = df[col].min()
                    max_val = df[col].max()
                    mean_val = df[col].mean()
                    context_parts.append(f"- {col}: {dtype} | Range: {min_val:.2f} to {max_val:.2f} (avg: {mean_val:.2f}) | {null_pct:.1f}% null")
                else:
                    context_parts.append(f"- {col}: {dtype} | All null values")
            except:
                context_parts.append(f"- {col}: {dtype} | {null_pct:.1f}% null")
    
    if len(df.columns) > 20:
        context_parts.append(f"... and {len(df.columns) - 20} more columns")
    
    # Sample data preview (more rows for better context)
    context_parts.append("\nSample Data (first 5 rows):")
    try:
        sample_data = df.head(5).to_string(max_cols=10, max_colwidth=50)
        context_parts.append(sample_data)
    except Exception:
        context_parts.append("Sample data preview unavailable")
    
    # Summary statistics for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        context_parts.append(f"\nNumeric Summary (showing {min(8, len(numeric_cols))} columns):")
        try:
            summary = df[numeric_cols[:8]].describe().round(2)
            context_parts.append(summary.to_string())
        except Exception:
            context_parts.append("Summary statistics unavailable")
    
    # Identify column types dynamically (no hardcoded assumptions)
    context_parts.append("\nColumn Analysis:")
    
    # Categorical columns
    categorical_cols = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    if categorical_cols:
        context_parts.append(f"- Text/Categorical columns ({len(categorical_cols)}): {', '.join(categorical_cols[:8])}")
        if len(categorical_cols) > 8:
            context_parts.append(f"  ...and {len(categorical_cols) - 8} more")
    
    # Numeric columns
    if len(numeric_cols) > 0:
        integer_cols = df.select_dtypes(include=['int64', 'int32', 'int16', 'int8']).columns.tolist()
        float_cols = df.select_dtypes(include=['float64', 'float32', 'float16']).columns.tolist()
        
        if integer_cols:
            context_parts.append(f"- Integer columns ({len(integer_cols)}): {', '.join(integer_cols[:6])}")
        if float_cols:
            context_parts.append(f"- Float columns ({len(float_cols)}): {', '.join(float_cols[:6])}")
    
    # Date columns
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    if date_cols:
        context_parts.append(f"- Date/Time columns ({len(date_cols)}): {', '.join(date_cols[:5])}")
    
    # Data quality insights
    context_parts.append("\nData Quality:")
    total_nulls = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]
    null_percentage = (total_nulls / total_cells * 100) if total_cells > 0 else 0
    context_parts.append(f"- Overall missing data: {null_percentage:.1f}% ({total_nulls:,} out of {total_cells:,} cells)")
    
    # Columns with high null percentage
    high_null_cols = df.columns[df.isnull().sum() / len(df) > 0.5].tolist()
    if high_null_cols:
        context_parts.append(f"- Columns with >50% missing: {', '.join(high_null_cols[:5])}")
    
    return "\n".join(context_parts)

def analyze_data_patterns(df):
    """
    Analyze data patterns without making assumptions about content.
    This provides insights that help the AI understand relationships.
    """
    insights = []
    
    # Correlation analysis for numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 1:
        try:
            corr_matrix = df[numeric_cols].corr()
            # Find highly correlated pairs
            high_corr_pairs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    corr_val = corr_matrix.iloc[i, j]
                    if abs(corr_val) > 0.7:  # Strong correlation
                        col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                        high_corr_pairs.append(f"{col1} ↔ {col2} ({corr_val:.2f})")
            
            if high_corr_pairs:
                insights.append(f"Strong correlations found: {'; '.join(high_corr_pairs[:3])}")
        except:
            pass
    
    # Unique value analysis
    low_cardinality_cols = []
    high_cardinality_cols = []
    
    for col in df.columns:
        unique_count = df[col].nunique()
        total_count = len(df)
        if total_count > 0:
            unique_ratio = unique_count / total_count
            if unique_ratio < 0.05 and unique_count < 20:  # Low cardinality
                low_cardinality_cols.append(f"{col}({unique_count})")
            elif unique_ratio > 0.95:  # High cardinality (likely IDs)
                high_cardinality_cols.append(col)
    
    if low_cardinality_cols:
        insights.append(f"Low cardinality columns (good for grouping): {', '.join(low_cardinality_cols[:5])}")
    
    if high_cardinality_cols:
        insights.append(f"High cardinality columns (likely identifiers): {', '.join(high_cardinality_cols[:5])}")
    
    return insights