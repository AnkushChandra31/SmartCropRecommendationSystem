"""Dataset creation and loading functions."""

import os

import numpy as np
import pandas as pd

from crop import FEATURES

DATA_FILE = "crop_data.csv"


def create_demo_dataset():
    """Create sample crop data when no CSV file is available."""
    crop_values = {
        "rice": [90, 42, 40, 27, 82, 6.5, 220],
        "maize": [78, 48, 22, 24, 66, 6.2, 85],
        "chickpea": [40, 62, 78, 21, 22, 7.2, 65],
        "banana": [105, 80, 48, 28, 80, 6.2, 105],
        "cotton": [115, 45, 20, 25, 80, 6.8, 80],
        "coffee": [100, 28, 28, 24, 55, 6.9, 150],
    }
    rng = np.random.default_rng(42)
    rows = []
    for crop_name, values in crop_values.items():
        for _ in range(30):
            row = rng.normal(values, [8, 8, 8, 1.5, 5, 0.3, 12]).round(2)
            row[:3] = np.maximum(row[:3], 0)
            row[4] = np.clip(row[4], 10, 100)
            row[5] = np.clip(row[5], 3.5, 9)
            row[6] = np.maximum(row[6], 0)
            rows.append([*row, crop_name])
    pd.DataFrame(rows, columns=FEATURES + ["label"]).to_csv(DATA_FILE, index=False)


def get_crop_data():
    """Return the project CSV data, creating a demo file if needed."""
    if not os.path.exists(DATA_FILE):
        create_demo_dataset()
    return pd.read_csv(DATA_FILE)
