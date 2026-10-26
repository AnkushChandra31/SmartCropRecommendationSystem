# Smart Crop Recommendation System

This is a basic college project using separate, easy-to-understand Python files.

## Install

```powershell
pip install pandas scikit-learn
```

## Run

```powershell
python main.py
```

The program opens a simple GUI. Enter N, P, K, temperature, humidity, soil pH, and rainfall, then click **Recommend Crop**.

## Files

- `main.py` - starts the project
- `gui.py` - GUI screen and buttons
- `recommendation_system.py` - ML training and prediction
- `data_structures.py` - CSV dataset functions
- `crop.py` - input field names
- `farmer.py` - stores farmer input
- `notification.py` - error message box

The first run creates `crop_data.csv` automatically. You can replace it with your own CSV later; keep these columns:

`N, P, K, temperature, humidity, ph, rainfall, label`
