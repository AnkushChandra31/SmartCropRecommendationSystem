# Smart Crop Recommendation System (Phase 1 - Terminal)

Recommends a crop from soil values (N, P, K, pH) and live weather
(temperature, humidity, rainfall) using a Random Forest model.

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
| `main.py` | Terminal menu: asks for input, shows the result |
| `crop_recommender.py` | ML steps: load, clean, split, train, evaluate, predict |
| `weather_service.py` | Gets weather from the Open-Meteo API (no key needed) |

## Phase 2 plan (from the synopsis)
- [ ] Add Decision Tree and KNN, compare with Random Forest (`build_model`)
- [ ] Add precision, recall, F1-score, confusion matrix (`evaluate_model`)
- [ ] Add EDA graphs with Matplotlib / Seaborn (new file `eda.py`)
- [ ] Better preprocessing: outliers, data types (`clean_data`)
- [ ] Streamlit interface (new file `app.py`, reuse `crop_recommender.py`)