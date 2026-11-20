# Smart Crop Recommendation System

Desktop GUI that recommends a crop from soil values (N, P, K, pH) and live weather
(temperature, humidity, rainfall) using a Random Forest model. It also shows
a seven-day rain prediction, crop health details, and future crop-care advice.

## Setup
```
pip install -r requirements.txt
```
Put the dataset `crop_data.csv` in this folder. It needs these columns:
`N, P, K, temperature, humidity, ph, rainfall, label`
(the standard Kaggle "Crop Recommendation Dataset").

## Run
```
python main.py
```

## Files
| File | What it does |
|------|--------------|
| `main.py` | Starts the desktop application |
| `gui.py` | Desktop GUI: soil input, weather, result, health, and future details |
| `crop_recommender.py` | ML steps: load, clean, split, train, evaluate, predict |
| `weather_service.py` | Gets weather from the Open-Meteo API (no key needed) |
| `crop_health.py` | Checks crop health and gives future care advice |

## New features
- Seven-day rainfall prediction from Open-Meteo.
- Crop health status based on the selected crop's dataset ranges.
- Future care advice for irrigation, drainage, soil correction, and monitoring.
