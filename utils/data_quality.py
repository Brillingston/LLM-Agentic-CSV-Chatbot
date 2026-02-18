import pandas as pd
import numpy as np
from typing import Dict, List, Any
import re


def check_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect columns with missing values"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df) * 100).round(2)
    
    issues = []
    for col in df.columns:
        if missing[col] > 0:
            issues.append({
                'column': col,
                'missing_count': int(missing[col]),
                'missing_percent': float(missing_pct[col])
            })
    
    return {
        'type': 'missing_values',
        'severity': 'warning' if issues else 'pass',
        'issues': issues
    }


def check_duplicates(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect duplicate rows"""
    duplicates = df.duplicated().sum()
    
    return {
        'type': 'duplicate_rows',
        'severity': 'error' if duplicates > 0 else 'pass',
        'count': int(duplicates)
    }


def check_duplicate_ids(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect potential ID columns with duplicates"""
    issues = []
    
    # Look for columns that might be IDs
    id_patterns = ['id', 'customer', 'user', 'order', 'transaction', 'account', 'employee']
    
    for col in df.columns:
        col_lower = col.lower()
        if any(pattern in col_lower for pattern in id_patterns):
            duplicates = df[col].duplicated()
            if duplicates.any():
                dup_values = df[col][duplicates].unique().tolist()[:5]  # Show first 5
                issues.append({
                    'column': col,
                    'duplicate_values': dup_values,
                    'count': int(duplicates.sum())
                })
    
    return {
        'type': 'duplicate_ids',
        'severity': 'error' if issues else 'pass',
        'issues': issues
    }


def check_outliers(df: pd.DataFrame, threshold: float = 3.0) -> Dict[str, Any]:
    """Detect statistical outliers in numeric columns"""
    issues = []
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        values = df[col].dropna()
        if len(values) < 10:  # Skip if too few values
            continue
        
        mean = values.mean()
        std = values.std()
        
        if std == 0:  # Skip if no variation
            continue
        
        # Z-score method
        z_scores = np.abs((values - mean) / std)
        outliers = values[z_scores > threshold]
        
        if len(outliers) > 0:
            issues.append({
                'column': col,
                'outlier_count': int(len(outliers)),
                'outlier_values': outliers.head(3).tolist(),
                'threshold_std': threshold
            })
    
    return {
        'type': 'outliers',
        'severity': 'warning' if issues else 'pass',
        'issues': issues
    }


def check_date_formats(df: pd.DataFrame) -> Dict[str, Any]:
    """Detect date-like columns not in datetime format"""
    issues = []
    
    date_patterns = ['date', 'time', 'created', 'updated', 'timestamp', 'year', 'month']
    
    for col in df.columns:
        col_lower = col.lower()
        
        # Check if column name suggests it's a date
        if any(pattern in col_lower for pattern in date_patterns):
            # Check if it's not already datetime
            if df[col].dtype == 'object':
                # Sample first non-null value
                sample = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                
                if sample:
                    issues.append({
                        'column': col,
                        'current_type': str(df[col].dtype),
                        'sample_value': str(sample)
                    })
    
    return {
        'type': 'date_formats',
        'severity': 'warning' if issues else 'pass',
        'issues': issues
    }


def check_invalid_formats(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for common invalid formats (email, phone, etc.)"""
    issues = []
    
    # Email validation
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    for col in df.columns:
        if 'email' in col.lower():
            if df[col].dtype == 'object':
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    invalid_emails = non_null.apply(lambda x: not bool(email_pattern.match(str(x))))
                    invalid_count = invalid_emails.sum()
                    
                    if invalid_count > 0:
                        issues.append({
                            'column': col,
                            'type': 'email',
                            'invalid_count': int(invalid_count)
                        })
    
    # Phone validation (simple check for digits)
    for col in df.columns:
        if 'phone' in col.lower() or 'mobile' in col.lower():
            if df[col].dtype == 'object':
                non_null = df[col].dropna()
                if len(non_null) > 0:
                    # Should have at least 10 digits
                    invalid_phones = non_null.apply(lambda x: len(re.findall(r'\d', str(x))) < 10)
                    invalid_count = invalid_phones.sum()
                    
                    if invalid_count > 0:
                        issues.append({
                            'column': col,
                            'type': 'phone',
                            'invalid_count': int(invalid_count)
                        })
    
    return {
        'type': 'invalid_formats',
        'severity': 'error' if issues else 'pass',
        'issues': issues
    }


def check_column_names(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for problematic column names"""
    issues = []
    
    for col in df.columns:
        problems = []
        
        # Check for leading/trailing spaces
        if col != col.strip():
            problems.append('has leading/trailing spaces')
        
        # Check for special characters
        if not re.match(r'^[a-zA-Z0-9_\s&]+$', col):
            problems.append('contains special characters')
        
        # Check for very long names
        if len(col) > 50:
            problems.append('name is too long (>50 chars)')
        
        if problems:
            issues.append({
                'column': col,
                'problems': problems
            })
    
    return {
        'type': 'column_names',
        'severity': 'warning' if issues else 'pass',
        'issues': issues
    }


def generate_quality_report(df: pd.DataFrame) -> Dict[str, Any]:
    """Run all quality checks and generate comprehensive report"""
    
    checks = [
        check_missing_values(df),
        check_duplicates(df),
        check_duplicate_ids(df),
        check_outliers(df),
        check_date_formats(df),
        check_invalid_formats(df),
        check_column_names(df)
    ]
    
    # Categorize by severity
    passed = [c for c in checks if c['severity'] == 'pass']
    warnings = [c for c in checks if c['severity'] == 'warning']
    errors = [c for c in checks if c['severity'] == 'error']
    
    return {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'checks_run': len(checks),
        'passed': passed,
        'warnings': warnings,
        'errors': errors,
        'overall_health': 'Good' if not errors and len(warnings) <= 1 else 'Fair' if not errors else 'Poor'
    }


def format_quality_report(report: Dict[str, Any]) -> str:
    """Format the quality report as readable markdown"""
    
    output = []
    output.append("## 📊 Data Quality Report\n")
    output.append(f"**Overall Health**: {report['overall_health']}")
    output.append(f"**Dataset**: {report['total_rows']:,} rows × {report['total_columns']} columns\n")
    
    # Passed checks
    if report['passed']:
        output.append("### ✅ Passed Checks")
        for check in report['passed']:
            if check['type'] == 'duplicate_rows':
                output.append(f"- No duplicate rows detected")
            elif check['type'] == 'column_names':
                output.append(f"- All column names are valid")
            elif check['type'] == 'missing_values':
                output.append(f"- No missing values detected")
            elif check['type'] == 'duplicate_ids':
                output.append(f"- No duplicate IDs found")
            elif check['type'] == 'outliers':
                output.append(f"- No statistical outliers detected")
            elif check['type'] == 'date_formats':
                output.append(f"- All date columns properly formatted")
            elif check['type'] == 'invalid_formats':
                output.append(f"- All format validations passed")
        output.append("")
    
    # Warnings
    if report['warnings']:
        output.append("### ⚠️ Warnings")
        for check in report['warnings']:
            if check['type'] == 'missing_values':
                for issue in check['issues']:
                    output.append(f"- **{issue['column']}**: {issue['missing_count']} missing values ({issue['missing_percent']}%)")
            
            elif check['type'] == 'outliers':
                for issue in check['issues']:
                    values_str = ", ".join([f"{v:,.2f}" for v in issue['outlier_values']])
                    output.append(f"- **{issue['column']}**: {issue['outlier_count']} outliers detected (e.g., {values_str})")
            
            elif check['type'] == 'date_formats':
                for issue in check['issues']:
                    output.append(f"- **{issue['column']}**: Looks like a date but stored as text (sample: {issue['sample_value']})")
            
            elif check['type'] == 'column_names':
                for issue in check['issues']:
                    problems = ", ".join(issue['problems'])
                    output.append(f"- **{issue['column']}**: {problems}")
        output.append("")
    
    # Errors
    if report['errors']:
        output.append("### ❌ Errors")
        for check in report['errors']:
            if check['type'] == 'duplicate_rows':
                output.append(f"- **{check['count']} duplicate rows** found in dataset")
            
            elif check['type'] == 'duplicate_ids':
                for issue in check['issues']:
                    dup_str = ", ".join(str(v) for v in issue['duplicate_values'][:3])
                    output.append(f"- **{issue['column']}**: {issue['count']} duplicates (e.g., {dup_str})")
            
            elif check['type'] == 'invalid_formats':
                for issue in check['issues']:
                    output.append(f"- **{issue['column']}**: {issue['invalid_count']} invalid {issue['type']} formats")
        output.append("")
    
    # Recommendations
    if report['warnings'] or report['errors']:
        output.append("### 💡 Recommendations")
        
        if any(c['type'] == 'missing_values' for c in report['warnings']):
            output.append("- Consider handling missing values before analysis (fill, drop, or filter)")
        
        if any(c['type'] == 'duplicate_ids' for c in report['errors']):
            output.append("- Review and resolve duplicate IDs to ensure data integrity")
        
        if any(c['type'] == 'date_formats' for c in report['warnings']):
            output.append("- Convert date columns to datetime format for time-based queries")
        
        if any(c['type'] == 'outliers' for c in report['warnings']):
            output.append("- Investigate outlier values - they may be data entry errors")
        
        if any(c['type'] == 'invalid_formats' for c in report['errors']):
            output.append("- Clean invalid format entries for better data quality")
    
    return "\n".join(output)