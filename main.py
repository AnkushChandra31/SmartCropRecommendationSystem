"""Start the Smart Crop Recommendation System."""

from gui import CropGUI
from recommendation_system import CropRecommendationSystem


if __name__ == "__main__":
    system = CropRecommendationSystem()
    app = CropGUI(system)
    app.run()
