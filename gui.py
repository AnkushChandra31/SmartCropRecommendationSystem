"""Tkinter GUI for the crop recommendation project."""

import tkinter as tk

from crop import FEATURES, FIELD_NAMES
from notification import show_input_error


class CropGUI:
    def __init__(self, system):
        self.system = system
        self.entries = {}
        self.root = tk.Tk()
        self.root.title("Smart Crop Recommendation System")
        self.root.geometry("480x500")
        self.root.configure(bg="#eaf5ea")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Smart Crop Recommendation System", font=("Arial", 16, "bold"),
                 bg="#eaf5ea", fg="#1b5e20").pack(pady=(18, 5))
        tk.Label(self.root, text=f"Random Forest model accuracy: {self.system.accuracy:.1f}%",
                 font=("Arial", 10), bg="#eaf5ea").pack(pady=(0, 14))

        form = tk.Frame(self.root, bg="#eaf5ea")
        form.pack(padx=35, fill="x")
        for row, feature in enumerate(FEATURES):
            tk.Label(form, text=FIELD_NAMES[feature], font=("Arial", 10), bg="#eaf5ea").grid(
                row=row, column=0, sticky="w", pady=5
            )
            entry = tk.Entry(form, width=18, font=("Arial", 10))
            entry.grid(row=row, column=1, padx=(20, 0), pady=5)
            self.entries[feature] = entry

        tk.Button(self.root, text="Recommend Crop", font=("Arial", 11, "bold"),
                  bg="#2e7d32", fg="white", command=self.recommend).pack(pady=20)
        self.result_label = tk.Label(self.root, text="Enter values and click Recommend Crop",
                                     font=("Arial", 13, "bold"), bg="#eaf5ea", fg="#1b5e20")
        self.result_label.pack(pady=8)

    def recommend(self):
        try:
            values = {feature: self.entries[feature].get() for feature in FEATURES}
            crop_name = self.system.recommend_crop(values)
            self.result_label.config(text=f"Recommended Crop: {crop_name.title()}")
        except ValueError:
            show_input_error()

    def run(self):
        self.root.mainloop()
