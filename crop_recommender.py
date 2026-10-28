import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score


FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

TARGET = "label"


def load_data(path="crop_data.csv"):
    data = pd.read_csv(path)

    data.columns = data.columns.str.strip()

    missing = set(FEATURES + [TARGET]) - set(data.columns)
    if missing:
        raise ValueError("Dataset is missing columns: " + ", ".join(sorted(missing)))

    return data


def clean_data(data):
    data = data.dropna(subset=FEATURES + [TARGET])  
    data = data.drop_duplicates()                    
    return data


def split_data(data):
    X = data[FEATURES]   # inputs
    y = data[TARGET]     # crop name

    return train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y       
    )


def build_model():
    return RandomForestClassifier(n_estimators=100, random_state=42)


def train_model(model, X_train, y_train):
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions) * 100

    return accuracy


def recommend_crop(model, values):
    """values is a dictionary with all 7 FEATURES as keys."""
    row = [[float(values[name]) for name in FEATURES]]
    input_data = pd.DataFrame(row, columns=FEATURES)
    return model.predict(input_data)[0]


def train_system(path="crop_data.csv"):
    data = load_data(path)
    data = clean_data(data)

    X_train, X_test, y_train, y_test = split_data(data)

    model = build_model()
    model = train_model(model, X_train, y_train)

    accuracy = evaluate_model(model, X_test, y_test)

    return model, accuracy