import tkinter as tk
from tkinter import messagebox
import requests
import geocoder
from datetime import datetime

NOT_FOUND_ERROR = -1
EXCEPTION_ERROR = -2

def get_coordinates_from_a_query(query):
    """Use Open-Meteo geocoding API to resolve name, ZIP, or coords."""
    try:
        # If query looks like lat,lon
        if "," in query:
            latitude, longtitude = query.split(",")
            return float(latitude.strip()), float(longtitude.strip()), query

        url = f"https://geocoding-api.open-meteo.com/v1/search?name={query}&count=1&language=en&format=json"
        r = requests.get(url).json()
        if "results" in r and len(r["results"]) > 0:
            res = r["results"][0]
            return res["latitude"], res["longitude"], f"{res['name']}, {res.get('country_code','')}"
        else:
            return None
    except Exception:
        return None


def get_weather(lat, lon):
    """Fetch weather data from Open-Meteo."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,apparent_temperature,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,wind_direction_10m"
        f"&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code"
        f"&timezone=auto"
    )
    r = requests.get(url).json()
    return r


def fetch_weather():
    query = entry.get().strip()
    if not query:
        messagebox.showerror("Error", "Please enter a location")
        return

    coords = get_coordinates_from_a_query(query)
    if not coords:
        messagebox.showerror("Error", "Location not found")
        return

    lat, lon, place = coords
    data = get_weather(lat, lon)

    if "current" not in data:
        messagebox.showerror("Error", "Weather data not available")
        return

    # Display current weather
    current = data["current"]
    result = f"Weather for {place}\n\n"
    result += f"Temperature is {current['temperature_2m']}°C (Feels {current['apparent_temperature']}°C)\n"
    result += f"Humidity is {current['relative_humidity_2m']}%\n"
    result += f"Precipipitation is {current['precipitation']} mm\n"
    result += f"Wind speed is {current['wind_speed_10m']} km/h ({current['wind_direction_10m']}°)\n\n"

    # Forecast
    result += "5-Day Forecast:\n"
    for i in range(5):
        date = data["daily"]["time"][i]
        tmax = data["daily"]["temperature_2m_max"][i]
        tmin = data["daily"]["temperature_2m_min"][i]
        precip = data["daily"]["precipitation_sum"][i]
        result += f"{date}: {tmin}°C - {tmax}°C, Precip {precip} mm\n"

    text.delete(1.0, tk.END)
    text.insert(tk.END, result)


def use_my_location():
    g = geocoder.ip("me")
    if not g.ok:
        messagebox.showerror("Error", "Could not detect your location")
        return
    lat, lon = g.latlng
    data = get_weather(lat, lon)
    place = f"My Location ({round(lat,2)}, {round(lon,2)})"

    # Current weather
    current = data["current"]
    result = f"Weather for {place}\n\n"
    result += f"Temperature is {current['temperature_2m']}°C (Feels {current['apparent_temperature']}°C)\n"
    result += f"Humidity is {current['relative_humidity_2m']}%\n"
    result += f"Precipipitation is {current['precipitation']} mm\n"
    result += f"Wind speed is {current['wind_speed_10m']} km/h ({current['wind_direction_10m']}°)\n\n"


    # Forecast
    result += "5-Day Forecast:\n"
    for i in range(5):
        date = data["daily"]["time"][i]
        tmax = data["daily"]["temperature_2m_max"][i]
        tmin = data["daily"]["temperature_2m_min"][i]
        precip = data["daily"]["precipitation_sum"][i]
        result += f"{date}: {tmin}°C - {tmax}°C, Precip {precip} mm\n"

    text.delete(1.0, tk.END)
    text.insert(tk.END, result)


# GUI setup
root = tk.Tk()
root.title("Weather App")
root.geometry("500x500")

frame = tk.Frame(root)
frame.pack(pady=10)

entry = tk.Entry(frame, width=30, font=("Arial", 14))
entry.pack(side=tk.LEFT, padx=5)

btn = tk.Button(frame, text="Search", command=fetch_weather)
btn.pack(side=tk.LEFT)

loc_btn = tk.Button(root, text="Use My Location", command=use_my_location)
loc_btn.pack(pady=5)

text = tk.Text(root, wrap=tk.WORD, font=("Arial", 12))
text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

root.mainloop()
