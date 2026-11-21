
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

from crop_health import DISPLAY_NAMES, get_crop_health, get_future_advice
from crop_recommender import recommend_crop, train_system
from weather_service import get_weather

BG = "#f1f6f2"
CARD = "#ffffff"
BORDER = "#dce7df"
DARK = "#154734"
GREEN = "#237a57"
GREEN_HOVER = "#185d40"
TEXT = "#2b4036"
MUTED = "#68766e"
TILE = "#edf7f0"
AMBER = "#b7791f"
RED = "#c0392b"
BLUE = "#2f80b7"
FONT = "Segoe UI"

SOIL_FIELDS = [
    ("N", "Nitrogen (N)", "kg/ha, typically 0 - 140", 0, 500),
    ("P", "Phosphorus (P)", "kg/ha, typically 5 - 145", 0, 500),
    ("K", "Potassium (K)", "kg/ha, typically 5 - 205", 0, 500),
    ("ph", "Soil pH", "scale 0 - 14, typically 3.5 - 9.9", 0, 14),
]

STATUS_COLORS = {
    "Healthy": GREEN,
    "Moderate - needs monitoring": AMBER,
    "Needs attention": RED,
}


class CropRecommendationGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart Crop Recommendation System")
        self.root.geometry("1100x860")
        self.root.minsize(980, 740)
        self.root.configure(bg=BG)

        self.model = None
        self.weather = None
        self.entries = {}
        self.hint_labels = {}
        self.forecast = []
        self.chart_mode = "rain"
        self._busy = 0

        self.status_text = tk.StringVar(value="Training the crop model...")
        self.crop_text = tk.StringVar(value="—")
        self.health_text = tk.StringVar(value="Not checked yet")

        self._setup_style()
        self._build_screen()
        self._begin_busy()
        threading.Thread(target=self._train_model, daemon=True).start()

    def _setup_style(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TEntry", padding=6, fieldbackground="white", bordercolor=BORDER)
        style.configure("Status.TLabel", font=(FONT, 9), foreground=MUTED, background=BG)
        style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor=BORDER, background=GREEN, bordercolor=BG, lightcolor=GREEN, darkcolor=GREEN,
        )

    def _button(self, parent, text, command, primary=True):
        bg, hover, fg = (GREEN, GREEN_HOVER, "white") if primary else ("#e4efe8", "#d3e5da", DARK)
        btn = tk.Button(
            parent, text=text, command=command, bg=bg, fg=fg, activebackground=hover,
            activeforeground=fg, relief="flat", bd=0, cursor="hand2",
            font=(FONT, 10, "bold"), padx=16, pady=8,
        )
        btn.bind("<Enter>", lambda _e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda _e: btn.config(bg=bg))
        return btn

    def _card(self, parent, title, subtitle, row, column, columnspan=1, **grid):
        outer = tk.Frame(parent, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        outer.grid(row=row, column=column, columnspan=columnspan, sticky="nsew", padx=8, pady=8, **grid)
        tk.Label(outer, text=title, bg=CARD, fg=DARK, font=(FONT, 12, "bold")).pack(anchor="w", padx=18, pady=(14, 0))
        tk.Label(outer, text=subtitle, bg=CARD, fg=MUTED, font=(FONT, 9), wraplength=420, justify="left").pack(
            anchor="w", padx=18, pady=(2, 8)
        )
        body = tk.Frame(outer, bg=CARD)
        body.pack(fill="both", expand=True, padx=18, pady=(0, 16))
        return body

    def _build_screen(self):
        header = tk.Frame(self.root, bg=DARK)
        header.pack(fill="x")
        tk.Label(header, text="🌱  Smart Crop Recommendation System", bg=DARK, fg="white",
                 font=(FONT, 20, "bold")).pack(anchor="w", padx=28, pady=(18, 0))
        tk.Label(header, text="Soil values + live weather → crop suggestion, health check and a 7-day care plan.",
                 bg=DARK, fg="#bfe0cd", font=(FONT, 10)).pack(anchor="w", padx=28, pady=(2, 16))

        # Status bar first so it keeps its space at the bottom.
        bar = tk.Frame(self.root, bg=BG)
        bar.pack(side="bottom", fill="x", padx=20, pady=(0, 10))
        ttk.Label(bar, textvariable=self.status_text, style="Status.TLabel").pack(side="left")
        self.progress = ttk.Progressbar(bar, mode="indeterminate", length=120, style="Green.Horizontal.TProgressbar")
        self.progress.pack(side="right")

        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=8)
        main.columnconfigure(0, weight=1, uniform="col")
        main.columnconfigure(1, weight=1, uniform="col")
        main.rowconfigure(1, weight=1)

        self._build_soil_card(self._card(main, "1. Soil details", "Enter the values from your soil test report.", 0, 0))
        self._build_weather_card(self._card(
            main, "2. Weather & rainfall", "Enter a city to fetch current weather and the next 7 days of rain.", 0, 1))
        self._build_result_card(self._card(main, "3. Recommendation & crop health", "", 1, 0, columnspan=2))

    def _build_soil_card(self, body):
        form = tk.Frame(body, bg=CARD)
        form.pack(fill="x")
        form.columnconfigure(1, weight=1)
        for row, (key, label, hint, _lo, _hi) in enumerate(SOIL_FIELDS):
            tk.Label(form, text=label, bg=CARD, fg=TEXT, font=(FONT, 10, "bold")).grid(
                row=row * 2, column=0, sticky="w", pady=(6, 0))
            entry = ttk.Entry(form, width=16, font=(FONT, 10))
            entry.grid(row=row * 2, column=1, sticky="ew", padx=(16, 0), pady=(6, 0))
            entry.bind("<Return>", lambda _e: self.get_recommendation())
            entry.bind("<KeyRelease>", lambda _e, k=key: self._clear_error(k))
            self.entries[key] = entry
            hint_label = tk.Label(form, text=hint, bg=CARD, fg=MUTED, font=(FONT, 8))
            hint_label.grid(row=row * 2 + 1, column=1, sticky="w", padx=(16, 0))
            self.hint_labels[key] = (hint_label, hint)

        buttons = tk.Frame(body, bg=CARD)
        buttons.pack(fill="x", pady=(12, 0))
        self._button(buttons, "Load example", self._load_example, primary=False).pack(side="left")
        self._button(buttons, "Clear", self._clear_inputs, primary=False).pack(side="left", padx=8)

    def _build_weather_card(self, body):
        line = tk.Frame(body, bg=CARD)
        line.pack(fill="x")
        self.city_entry = ttk.Entry(line, font=(FONT, 10))
        self.city_entry.pack(side="left", fill="x", expand=True, ipady=2)
        self.city_entry.insert(0, "Dehradun")
        self.city_entry.bind("<Return>", lambda _e: self.fetch_weather())
        self.fetch_btn = self._button(line, "Fetch Weather", self.fetch_weather)
        self.fetch_btn.pack(side="left", padx=(8, 0))

        tiles = tk.Frame(body, bg=CARD)
        tiles.pack(fill="x", pady=(12, 8))
        self.tile_vars = {}
        for i, (key, title) in enumerate([("city", "Location"), ("temp", "Temperature"),
                                          ("hum", "Humidity"), ("rain", "Rain (model input)")]):
            tiles.columnconfigure(i, weight=1, uniform="tile")
            tile = tk.Frame(tiles, bg=TILE)
            tile.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 6, 0))
            tk.Label(tile, text=title, bg=TILE, fg=MUTED, font=(FONT, 8)).pack(anchor="w", padx=8, pady=(6, 0))
            var = tk.StringVar(value="—")
            tk.Label(tile, textvariable=var, bg=TILE, fg=DARK, font=(FONT, 11, "bold")).pack(anchor="w", padx=8, pady=(0, 6))
            self.tile_vars[key] = var

        head = tk.Frame(body, bg=CARD)
        head.pack(fill="x")
        self.chart_title = tk.Label(head, text="Daily rainfall forecast (mm)", bg=CARD, fg=MUTED, font=(FONT, 9))
        self.chart_title.pack(side="left")
        self.mode_buttons = {}
        for mode, label in (("temp", "Temperature"), ("rain", "Rain")):
            btn = tk.Button(head, text=label, relief="flat", bd=0, cursor="hand2", font=(FONT, 9, "bold"),
                            padx=10, pady=2, command=lambda m=mode: self._set_chart_mode(m))
            btn.pack(side="right", padx=(4, 0))
            self.mode_buttons[mode] = btn
        self.chart = tk.Canvas(body, height=130, bg=CARD, highlightthickness=0)
        self.chart.pack(fill="both", expand=True)
        self.chart.bind("<Configure>", lambda _e: self._draw_chart())
        self._set_chart_mode("rain")

    def _build_result_card(self, body):
        top = tk.Frame(body, bg=CARD)
        top.pack(fill="x")
        self._button(top, "Get Crop Recommendation", self.get_recommendation).pack(side="left")
        self.crop_label = tk.Label(top, textvariable=self.crop_text, bg=TILE, fg=GREEN,
                                   font=(FONT, 16, "bold"), padx=16, pady=6)
        self.crop_label.pack(side="left", padx=(14, 0))
        self.health_label = tk.Label(top, textvariable=self.health_text, bg="#e6e9e7", fg=MUTED,
                                     font=(FONT, 10, "bold"), padx=12, pady=8)
        self.health_label.pack(side="left", padx=(10, 0))

        self.chips = tk.Frame(body, bg=CARD)
        self.chips.pack(fill="x", pady=(10, 4))
        self._render_chips(None)

        wrap = tk.Frame(body, bg=CARD, highlightbackground=BORDER, highlightthickness=1)
        wrap.pack(fill="both", expand=True, pady=(6, 0))
        scroll = ttk.Scrollbar(wrap, orient="vertical")
        self.detail_box = tk.Text(wrap, height=8, bg="white", fg=TEXT, relief="flat", wrap="word",
                                  font=(FONT, 10), padx=12, pady=10, yscrollcommand=scroll.set)
        scroll.config(command=self.detail_box.yview)
        scroll.pack(side="right", fill="y")
        self.detail_box.pack(side="left", fill="both", expand=True)
        self.detail_box.tag_configure("h", font=(FONT, 10, "bold"), foreground=DARK, spacing1=8, spacing3=2)
        self.detail_box.tag_configure("warn", foreground=RED, lmargin1=10, lmargin2=22)
        self.detail_box.tag_configure("ok", foreground=GREEN, lmargin1=10, lmargin2=22)
        self.detail_box.tag_configure("item", lmargin1=10, lmargin2=22)
        self._set_details([("Fetch the weather, enter your soil values, then click Get Crop Recommendation.", "item")])

    def _render_chips(self, good):
        for child in self.chips.winfo_children():
            child.destroy()
        tk.Label(self.chips, text="Conditions:", bg=CARD, fg=MUTED, font=(FONT, 9)).pack(side="left", padx=(0, 8))
        for name in DISPLAY_NAMES.values():
            if good is None:
                bg = "#e6e9e7"; fg = MUTED
            elif name in good:
                bg = GREEN; fg = "white"
            else:
                bg = RED; fg = "white"
            tk.Label(self.chips, text=name, bg=bg, fg=fg, font=(FONT, 9, "bold"), padx=9, pady=3).pack(side="left", padx=3)

    def _set_details(self, parts):
        self.detail_box.configure(state="normal")
        self.detail_box.delete("1.0", "end")
        for text, tag in parts:
            self.detail_box.insert("end", text + "\n", tag)
        self.detail_box.configure(state="disabled")

    def _draw_chart(self):
        c = self.chart
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        if w < 50 or h < 50:
            return
        if not self.forecast:
            c.create_text(w / 2, h / 2, text="Forecast will appear here after fetching weather.",
                          fill=MUTED, font=(FONT, 9))
            return
        if self.chart_mode == "temp":
            self._draw_temp_chart(c, w, h)
            return
        n = len(self.forecast)
        peak = max(5.0, max(d["rainfall"] for d in self.forecast))
        slot = w / n
        base, top = h - 22, 18
        for i, day in enumerate(self.forecast):
            x0 = i * slot + slot * 0.2
            x1 = (i + 1) * slot - slot * 0.2
            bar_h = (base - top) * (day["rainfall"] / peak)
            c.create_rectangle(x0, base - bar_h, x1, base, fill=BLUE if day["rainfall"] > 0.5 else "#b9cfdc", outline="")
            c.create_text((x0 + x1) / 2, base - bar_h - 8, text=f"{day['rainfall']:g}", fill=TEXT, font=(FONT, 8))
            try:
                label = datetime.strptime(day["date"], "%Y-%m-%d").strftime("%a %d")
            except ValueError:
                label = day["date"][5:]
            c.create_text((x0 + x1) / 2, h - 9, text=label, fill=MUTED, font=(FONT, 8))
        c.create_line(0, base, w, base, fill=BORDER)

    def _set_chart_mode(self, mode):
        self.chart_mode = mode
        self.chart_title.config(
            text="Daily rainfall forecast (mm)" if mode == "rain" else "Daily temperature forecast (°C)")
        for key, btn in self.mode_buttons.items():
            active = key == mode
            btn.config(bg=GREEN if active else "#e4efe8", fg="white" if active else DARK,
                       activebackground=GREEN_HOVER if active else "#d3e5da")
        self._draw_chart()

    def _day_label(self, date):
        try:
            return datetime.strptime(date, "%Y-%m-%d").strftime("%a %d")
        except ValueError:
            return date[5:]

    def _draw_temp_chart(self, c, w, h):
        days = self.forecast
        n = len(days)
        hi_vals = [d["max_temp"] for d in days]
        lo_vals = [d["min_temp"] for d in days]
        t_max, t_min = max(hi_vals) + 3, min(lo_vals) - 3
        left, right, top, base = 14, 14, 26, h - 22
        span = (t_max - t_min) or 1

        def xy(i, value):
            x = left + (w - left - right) * (i + 0.5) / n
            y = base - (base - top) * (value - t_min) / span
            return x, y

        for series, color, above in ((hi_vals, RED, True), (lo_vals, BLUE, False)):
            points = [xy(i, v) for i, v in enumerate(series)]
            if n > 1:
                c.create_line(*[coord for p in points for coord in p], fill=color, width=2, smooth=True)
            for (x, y), v in zip(points, series):
                c.create_oval(x - 3, y - 3, x + 3, y + 3, fill=color, outline="")
                c.create_text(x, y - 11 if above else y + 11, text=f"{v:.0f}°", fill=TEXT, font=(FONT, 8))
        for i, day in enumerate(days):
            c.create_text(xy(i, t_min)[0], h - 9, text=self._day_label(day["date"]), fill=MUTED, font=(FONT, 8))
        c.create_line(0, base, w, base, fill=BORDER)
        c.create_text(w - 14, 8, text="● Max", fill=RED, font=(FONT, 8, "bold"), anchor="e")
        c.create_text(w - 62, 8, text="● Min", fill=BLUE, font=(FONT, 8, "bold"), anchor="e")

    def _temperature_note(self):
        if not self.forecast:
            return "No temperature forecast available."
        lowest = min(d["min_temp"] for d in self.forecast)
        highest = max(d["max_temp"] for d in self.forecast)
        note = f"Expected range this week: {lowest:.0f}°C to {highest:.0f}°C."
        if lowest <= 4:
            note += " Frost risk: protect seedlings and young plants on the coldest nights."
        if highest >= 38:
            note += " Heat stress risk: irrigate in the early morning or evening and consider mulching."
        return note

    def _begin_busy(self):
        self._busy += 1
        self.progress.start(12)

    def _end_busy(self):
        self._busy = max(0, self._busy - 1)
        if self._busy == 0:
            self.progress.stop()

    def _clear_error(self, key):
        label, hint = self.hint_labels[key]
        label.config(text=hint, fg=MUTED)

    def _show_error(self, key, message):
        label, _hint = self.hint_labels[key]
        label.config(text=message, fg=RED)

    def _load_example(self):
        for key, value in {"N": "90", "P": "42", "K": "43", "ph": "6.5"}.items():
            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, value)
            self._clear_error(key)

    def _clear_inputs(self):
        for key, entry in self.entries.items():
            entry.delete(0, "end")
            self._clear_error(key)
        self.crop_text.set("—")
        self.health_text.set("Not checked yet")
        self.health_label.config(bg="#e6e9e7", fg=MUTED)
        self._render_chips(None)
        self._set_details([("Fetch the weather, enter your soil values, then click Get Crop Recommendation.", "item")])

    def _train_model(self):
        try:
            model, accuracy = train_system("crop_data.csv")
            self.root.after(0, lambda: self._model_ready(model, accuracy))
        except Exception as error:
            message = str(error)  
            self.root.after(0, lambda: self._model_failed(message))

    def _model_ready(self, model, accuracy):
        self.model = model
        self._end_busy()
        self.status_text.set(f"Model ready. Random Forest accuracy: {accuracy:.2f}%")

    def _model_failed(self, message):
        self._end_busy()
        self.status_text.set(f"Could not train model: {message}")
        messagebox.showerror("Model error", f"Could not train the model.\n\n{message}")

    def fetch_weather(self):
        city = self.city_entry.get().strip()
        if not city:
            messagebox.showwarning("City required", "Please enter a city name.")
            return
        self.fetch_btn.config(state="disabled")
        self.status_text.set(f"Fetching weather for {city}...")
        self._begin_busy()
        threading.Thread(target=self._load_weather, args=(city,), daemon=True).start()

    def _load_weather(self, city):
        try:
            weather = get_weather(city)
            self.root.after(0, lambda: self._weather_ready(weather))
        except Exception as error:
            message = str(error)
            self.root.after(0, lambda: self._weather_failed(message))

    def _weather_ready(self, weather):
        self._end_busy()
        self.fetch_btn.config(state="normal")
        self.weather = weather
        self.forecast = weather["rain_forecast"]
        self.tile_vars["city"].set(weather["city"])
        self.tile_vars["temp"].set(f"{weather['temperature']} °C")
        self.tile_vars["hum"].set(f"{weather['humidity']} %")
        self.tile_vars["rain"].set(f"{weather['rainfall']} mm")
        self._draw_chart()
        total = sum(d["rainfall"] for d in self.forecast)
        self.status_text.set(f"Weather loaded ({total:.1f} mm rain expected in 7 days). Enter soil details next.")

    def _weather_failed(self, message):
        self._end_busy()
        self.fetch_btn.config(state="normal")
        self.status_text.set("Weather could not be fetched. Check your internet or try another city.")
        messagebox.showerror("Weather unavailable", message)

    def _read_soil_values(self):
        values, ok = {}, True
        for key, label, _hint, lo, hi in SOIL_FIELDS:
            raw = self.entries[key].get().strip()
            try:
                number = float(raw)
            except ValueError:
                self._show_error(key, "Enter a number" if raw else "This field is required")
                ok = False
                continue
            if not lo <= number <= hi:
                self._show_error(key, f"Must be between {lo} and {hi}")
                ok = False
                continue
            values[key] = number
        return values if ok else None

    def get_recommendation(self):
        if not self.model:
            messagebox.showinfo("Please wait", "The model is still training. Please try again in a moment.")
            return
        if not self.weather:
            messagebox.showwarning("Weather required", "Please fetch the weather before continuing.")
            return
        soil = self._read_soil_values()
        if soil is None:
            self.status_text.set("Please fix the highlighted soil values.")
            return

        values = dict(soil)
        values["temperature"] = float(self.weather["temperature"])
        values["humidity"] = float(self.weather["humidity"])
        values["rainfall"] = float(self.weather["rainfall"])

        crop = recommend_crop(self.model, values)
        health = get_crop_health(self.model, crop, values)
        future = get_future_advice(health, self.weather["rain_forecast"])

        self.crop_text.set(f"🌾 {str(crop).title()}")
        color = STATUS_COLORS.get(health["status"], MUTED)
        self.health_text.set(f"{health['status']}  ·  {health['score']}/7")
        self.health_label.config(bg=color, fg="white")
        self._render_chips(health["good"])

        parts = [("Attention points", "h")]
        if health["attention"]:
            parts += [(f"⚠  {p}", "warn") for p in health["attention"]]
        else:
            parts.append(("✔  All key conditions are within the crop's suitable range.", "ok"))
        parts += [
            ("Next 7 days rainfall", "h"),
            (f"  {future['total_rain']} mm total across {future['rainy_days']} rainy day(s).", "item"),
            ("Temperature outlook", "h"),
            (f"  {self._temperature_note()}", "item"),
            ("Future care advice", "h"),
            (f"  {future['rain_advice']}", "item"),
            (f"  {future['health_advice']}", "item"),
        ]
        self._set_details(parts)
        self.status_text.set(f"Recommendation ready: {str(crop).title()}.")

    def run(self):
        self.root.mainloop()
