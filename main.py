
from crop_recommender import train_system, recommend_crop
from weather_service import get_weather


def ask_number(message, minimum=None, maximum=None):
    """Keep asking until the user types a valid number."""
    while True:
        text = input(message).strip()

        try:
            value = float(text)
        except ValueError:
            print("  Please enter a number.")
            continue

        if minimum is not None and value < minimum:
            print(f"  Value must be at least {minimum}.")
            continue
        if maximum is not None and value > maximum:
            print(f"  Value must be at most {maximum}.")
            continue

        return value


def get_soil_input():
    """Ask the user for soil values."""
    print("\n--- Soil details ---")
    n = ask_number("Nitrogen (N)   : ", minimum=0)
    p = ask_number("Phosphorus (P) : ", minimum=0)
    k = ask_number("Potassium (K)  : ", minimum=0)
    ph = ask_number("Soil pH (0-14) : ", minimum=0, maximum=14)
    return {"N": n, "P": p, "K": k, "ph": ph}


def get_weather_input():
    """Get weather from the internet. If that fails, ask the user to type it."""
    print("\n--- Weather ---")
    city = input("City: ").strip()

    try:
        print("Fetching weather data...")
        weather = get_weather(city)
    except Exception as error:
        print(f"Could not get weather automatically ({error})")
        print("Please enter the weather values yourself.")
        weather = {
            "temperature": ask_number("Temperature (C)          : "),
            "humidity": ask_number("Humidity (%)            : ", 0, 100),
            "rainfall": ask_number("Rainfall (mm, ~1 month) : ", minimum=0),
        }

    return weather


def show_result(crop, values):
    print("\n" + "=" * 40)
    print("INPUT SUMMARY")
    print("=" * 40)
    print(f"Nitrogen (N)  : {values['N']}")
    print(f"Phosphorus (P): {values['P']}")
    print(f"Potassium (K) : {values['K']}")
    print(f"Soil pH       : {values['ph']}")
    print(f"Temperature   : {values['temperature']} C")
    print(f"Humidity      : {values['humidity']} %")
    print(f"Rainfall      : {values['rainfall']} mm")
    print("-" * 40)
    print(f"RECOMMENDED CROP: {str(crop).upper()}")
    print("=" * 40)


def main():
    print("=" * 40)
    print(" Smart Crop Recommendation System")
    print("=" * 40)

    print("Training model, please wait...")
    try:
        model, accuracy = train_system("crop_data.csv")
    except FileNotFoundError:
        print("Error: 'crop_data.csv' not found. Put the dataset in this folder.")
        return
    except Exception as error:
        print(f"Error while training: {error}")
        return

    print(f"Model ready. Random Forest accuracy: {accuracy:.2f}%")

    while True:
        soil = get_soil_input()
        weather = get_weather_input()

        values = {**soil, **weather}  
        crop = recommend_crop(model, values)

        show_result(crop, values)

        again = input("\nTry another recommendation? (y/n): ").strip().lower()
        if again != "y":
            break

    print("Thank you for using the system!")


if __name__ == "__main__":
    main()