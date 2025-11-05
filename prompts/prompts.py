import csv
from pathlib import Path
import pandas as pd


def load_prompt(path: str, prompt_name: str) -> str:
    """
    Load a prompt from a CSV file by prompt name.
    
    Args:
        path: Path to the CSV file
        prompt_name: Name of the prompt to load (matches 'prompt_name' column)
    
    Returns:
        The prompt text as a string
    
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If prompt_name is not found
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Check if CSV has proper headers
        if 'prompt_name' not in reader.fieldnames:
            raise KeyError(
                f"CSV file must have 'prompt_name' and 'prompt' columns. "
                f"Found columns: {reader.fieldnames}"
            )
        
        for row in reader:
            if row.get('prompt_name') == prompt_name:
                return row.get('prompt', '')
        
    raise ValueError(f"Prompt '{prompt_name}' not found in CSV file")

def enrich_analyst_prompt(ANALYST_PROMPT: str, WEEKLY_DATA_PATH: str) -> str:
    weekly_data = pd.read_csv(WEEKLY_DATA_PATH)
    analyst_prompt = str(ANALYST_PROMPT).format(weekly_data=weekly_data)
    return analyst_prompt