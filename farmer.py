"""Small class for storing farmer-entered values."""

from crop import FEATURES


class FarmerInput:
    def __init__(self, values):
        self.values = values

    def to_list(self):
        return [float(self.values[feature]) for feature in FEATURES]
