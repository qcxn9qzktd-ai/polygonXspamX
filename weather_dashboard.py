"""
Weather Dashboard - Fetches and displays weather data from OpenWeatherMap API
"""

import requests
import json
from datetime import datetime
from typing import Dict, Optional, List
import os


class WeatherDashboard:
    """
    A weather dashboard that fetches data from OpenWeatherMap API.
    """
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str):
        """
        Initialize the weather dashboard with an API key.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "WeatherDashboard/1.0"})
    
    def get_current_weather(self, city: str, country_code: Optional[str] = None) -> Dict:
        """
        Fetch current weather for a specific city.
        
        Args:
            city: City name
            country_code: Optional ISO 3166 country code
        
        Returns:
            Dictionary containing weather data
        """
        location = f"{city},{country_code}" if country_code else city
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/weather",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}
    
    def get_forecast(self, city: str, country_code: Optional[str] = None, days: int = 5) -> Dict:
        """
        Fetch weather forecast for upcoming days.
        
        Args:
            city: City name
            country_code: Optional ISO 3166 country code
            days: Number of days to forecast (1-5 for free tier)
        
        Returns:
            Dictionary containing forecast data
        """
        location = f"{city},{country_code}" if country_code else city
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}
    
    def get_weather_by_coordinates(self, lat: float, lon: float) -> Dict:
        """
        Fetch weather by latitude and longitude.
        
        Args:
            lat: Latitude
            lon: Longitude
        
        Returns:
            Dictionary containing weather data
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}
    
    def format_current_weather(self, weather_data: Dict) -> str:
        """
        Format current weather data for display.
        
        Args:
            weather_data: Weather data dictionary
        
        Returns:
            Formatted weather string
        """
        if "error" in weather_data:
            return weather_data["error"]
        
        try:
            city = weather_data.get("name", "Unknown")
            country = weather_data.get("sys", {}).get("country", "")
            temp = weather_data.get("main", {}).get("temp", "N/A")
            feels_like = weather_data.get("main", {}).get("feels_like", "N/A")
            humidity = weather_data.get("main", {}).get("humidity", "N/A")
            pressure = weather_data.get("main", {}).get("pressure", "N/A")
            description = weather_data.get("weather", [{}])[0].get("description", "N/A")
            wind_speed = weather_data.get("wind", {}).get("speed", "N/A")
            clouds = weather_data.get("clouds", {}).get("all", "N/A")
            
            output = f"""
╔════════════════════════════════════════════╗
║          CURRENT WEATHER REPORT             ║
╚════════════════════════════════════════════╝

📍 Location: {city}, {country}
🌡️  Temperature: {temp}°C (feels like {feels_like}°C)
💧 Humidity: {humidity}%
🔽 Pressure: {pressure} hPa
☁️  Conditions: {description.capitalize()}
💨 Wind Speed: {wind_speed} m/s
☁️  Cloud Coverage: {clouds}%

Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            return output
        except (KeyError, TypeError) as e:
            return f"Error formatting weather data: {str(e)}"
    
    def format_forecast(self, forecast_data: Dict) -> str:
        """
        Format forecast data for display.
        
        Args:
            forecast_data: Forecast data dictionary
        
        Returns:
            Formatted forecast string
        """
        if "error" in forecast_data:
            return forecast_data["error"]
        
        try:
            city = forecast_data.get("city", {}).get("name", "Unknown")
            country = forecast_data.get("city", {}).get("country", "")
            forecasts = forecast_data.get("list", [])
            
            output = f"""
╔════════════════════════════════════════════╗
║          5-DAY WEATHER FORECAST             ║
╚════════════════════════════════════════════╝

📍 Location: {city}, {country}

"""
            for i, forecast in enumerate(forecasts[::8]):  # Every 8th forecast (daily)
                dt = datetime.fromtimestamp(forecast.get("dt", 0))
                temp = forecast.get("main", {}).get("temp", "N/A")
                description = forecast.get("weather", [{}])[0].get("description", "N/A")
                humidity = forecast.get("main", {}).get("humidity", "N/A")
                wind_speed = forecast.get("wind", {}).get("speed", "N/A")
                
                output += f"""
Day {i+1}: {dt.strftime('%A, %Y-%m-%d')}
  🌡️  Temp: {temp}°C
  ☁️  Conditions: {description.capitalize()}
  💧 Humidity: {humidity}%
  💨 Wind: {wind_speed} m/s
"""
            
            return output
        except (KeyError, TypeError) as e:
            return f"Error formatting forecast data: {str(e)}"
    
    def get_weather_alerts(self, city: str) -> List[str]:
        """
        Check for weather alerts in a city.
        
        Args:
            city: City name
        
        Returns:
            List of alert messages
        """
        weather = self.get_current_weather(city)
        alerts = []
        
        if "error" in weather:
            return [weather["error"]]
        
        try:
            temp = weather.get("main", {}).get("temp", 0)
            wind_speed = weather.get("wind", {}).get("speed", 0)
            description = weather.get("weather", [{}])[0].get("description", "").lower()
            
            # Temperature alerts
            if temp > 35:
                alerts.append("🔴 HEAT ALERT: Extreme heat warning!")
            elif temp < -15:
                alerts.append("❄️  COLD ALERT: Extreme cold warning!")
            
            # Wind alerts
            if wind_speed > 15:
                alerts.append("💨 WIND ALERT: Strong winds detected!")
            
            # Weather condition alerts
            if any(word in description for word in ["storm", "tornado", "severe"]):
                alerts.append("⛈️  SEVERE WEATHER: Storm warning!")
            elif "rain" in description and wind_speed > 10:
                alerts.append("🌧️  RAINSTORM: Heavy rain with strong winds!")
            
        except (KeyError, TypeError):
            alerts.append("Unable to process weather data for alerts")
        
        return alerts if alerts else ["✅ No weather alerts for this area"]


def main():
    """Main function to demonstrate the weather dashboard."""
    
    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        print("Error: OPENWEATHER_API_KEY environment variable not set")
        print("Get a free API key from: https://openweathermap.org/api")
        return
    
    # Initialize dashboard
    dashboard = WeatherDashboard(api_key)
    
    # Example: Get current weather
    print("\n" + "="*50)
    print("WEATHER DASHBOARD DEMO")
    print("="*50)
    
    cities = ["London", "New York", "Tokyo", "Sydney", "Paris"]
    
    for city in cities:
        print(f"\nFetching weather for {city}...")
        
        # Current weather
        current = dashboard.get_current_weather(city)
        print(dashboard.format_current_weather(current))
        
        # Weather alerts
        alerts = dashboard.get_weather_alerts(city)
        if alerts[0] != "✅ No weather alerts for this area":
            print("⚠️  ALERTS:")
            for alert in alerts:
                print(f"  {alert}")
        
        # Forecast
        forecast = dashboard.get_forecast(city)
        print(dashboard.format_forecast(forecast))
        
        print("\n" + "-"*50)


if __name__ == "__main__":
    main()
