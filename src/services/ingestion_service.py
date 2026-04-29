import pandas as pd
from src.data_processing.loader import get_dataframe
from src.data_processing.cleaner import clean_dataframe
from src.data_processing.transformer import transform_dataframe

def load_data(file_path: str = "data/raw/user_events.csv") -> pd.DataFrame:
    """Load raw data from CSV."""
    return get_dataframe(file_path)

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data."""
    return clean_dataframe(df)

def transform_data(df: pd.DataFrame) -> pd.DataFrame:
    """Transform data with funnel stages."""
    return transform_dataframe(df)

def save_data(df: pd.DataFrame, output_path: str = "data/processed/funnel_data.csv") -> None:
    """Save processed data to CSV."""
    df.to_csv(output_path, index=False)

def run_ingestion_pipeline(file_path: str = "data/raw/user_events.csv") -> pd.DataFrame:
    """Orchestrate the full ingestion pipeline."""
    df = load_data(file_path)
    df = clean_data(df)
    df = transform_data(df)
    save_data(df)
    return df