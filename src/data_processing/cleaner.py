import pandas as pd

def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicate records."""
    return df.drop_duplicates()

def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values in DataFrame."""
    return df.fillna(value={'product_id': None, 'device_type': None, 'source_channel': None})

def normalize_event_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize event names for consistency."""
    df['event_type'] = df['event_type'].str.lower().str.strip()
    return df

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning steps."""
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = normalize_event_names(df)
    return df