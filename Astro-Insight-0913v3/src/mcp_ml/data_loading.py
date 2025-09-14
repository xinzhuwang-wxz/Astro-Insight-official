import kagglehub
import yaml
import os

def load_config(config_path):
    """Loads YAML configuration file."""
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def download_data():
    """
    Downloads the Galaxy Zoo classification dataset from Kaggle.
    """
    print("Starting data download...")
    # The path where the data will be downloaded is managed by kagglehub,
    # typically ~/.cache/kagglehub/datasets/anjosut/galaxy-zoo-classification
    # config is passed as parameter, no need to reload
    
    path = kagglehub.dataset_download('anjosut/galaxy-zoo-classification')
    print(f"Data source import complete. Data downloaded to: {path}")
    return path
