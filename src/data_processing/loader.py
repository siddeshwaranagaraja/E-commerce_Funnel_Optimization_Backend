import pandas as pd
import os

REQUIRED_COLUMNS = ['user_id', 'session_id', 'event_type', 'timestamp']

def load_csv(file_path: str) -> pd.DataFrame:
    """Load CSV file and return DataFrame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    return pd.read_csv(file_path)

def validate_schema(df: pd.DataFrame) -> bool:
    """Validate DataFrame schema."""
    missing_cols = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    return True

def get_dataframe(file_path: str = "data/raw/user_events.csv") -> pd.DataFrame:
    """Return loaded and validated DataFrame."""
    df = load_csv(file_path)
    validate_schema(df)
    return df