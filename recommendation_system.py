"""Machine learning training and prediction code."""

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from crop import FEATURES
from data_structures import get_crop_data
from farmer import FarmerInput


class CropRecommendationSystem:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.accuracy = self.train_model()

    def train_model(self):
        data = get_crop_data()
        X = data[FEATURES]
        y = data["label"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        self.model.fit(X_train, y_train)
        return self.model.score(X_test, y_test) * 100

    def recommend_crop(self, values):
        farmer_input = FarmerInput(values)
        input_data = pd.DataFrame([farmer_input.to_list()], columns=FEATURES)
        return self.model.predict(input_data)[0]
