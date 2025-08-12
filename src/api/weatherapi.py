import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
from memory_profiler import profile


class WeatherAPI:

    def __init__(self, city=None, country=None, period=None):
        self.cache_session = requests_cache.CachedSession('.cache',
                                                          expire_after=3600)
        self.retry_session = retry(self.cache_session,
                                   retries=5,
                                   backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=self.retry_session)
        self.city = city
        self.country = country
        self.period = period

    def get_lat_lon(self, city: str, country: str = None) -> tuple:
        url = "https://geocoding-api.open-meteo.com/v1/search"
        params = {"name": city}
        if country:
            params["country"] = country
        response = self.retry_session.get(url,
                                          params=params)  # Use cached session
        data = response.json()
        if data.get("results"):
            lat = data["results"][0]["latitude"]
            lon = data["results"][0]["longitude"]
            country = data["results"][0]["country"]
            return lat, lon, country
        else:
            raise Exception("Location not found")

    def seconds_to_hours(self, seconds: int) -> float:
        return seconds / 3600

    @profile
    def get_hourly_forecast(self, latitude: float,
                            longitude: float) -> pd.DataFrame:
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ["temperature_2m", "rain", "wind_speed_10m", "visibility", "relative_humidity_2m"]
            }
            url = "https://api.open-meteo.com/v1/forecast"
            response = self.openmeteo.weather_api(url=url, params=params)[0]
            hourly = response.Hourly()

            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_rain = hourly.Variables(1).ValuesAsNumpy()
            hourly_visibility = hourly.Variables(2).ValuesAsNumpy()
            hourly_wind_speed_10m = hourly.Variables(3).ValuesAsNumpy()
            hourly_relative_humidity_2m = hourly.Variables(4).ValuesAsNumpy()

            times = pd.date_range(start=pd.to_datetime(hourly.Time(),
                                                       unit="s",
                                                       utc=True),
                                  end=pd.to_datetime(hourly.TimeEnd(),
                                                     unit="s",
                                                     utc=True),
                                  freq=pd.Timedelta(seconds=hourly.Interval()),
                                  inclusive="left")

            hourly_data = {
                "Date": times.astype(str),
                "Temperature(°C)": hourly_temperature_2m,
                "Rain(mm)": hourly_rain,
                "Wind Speed(m/s)": hourly_wind_speed_10m,
                "Visibility(m)": hourly_visibility,
                "Humidity(%)": hourly_relative_humidity_2m
            }

            hourly_dataframe = pd.DataFrame(data=hourly_data)
            hourly_dataframe = hourly_dataframe.iloc[:24]  # Limit to 24 hours
            return hourly_dataframe
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})

    @profile
    def get_daily_forecast(self, latitude: float,
                           longitude: float) -> pd.DataFrame:
        try:
            params = {
                "latitude":
                latitude,
                "longitude":
                longitude,
                "daily": [
                    "temperature_2m_max", "temperature_2m_min", "rain_sum",
                    "wind_speed_10m_max","sunrise", "sunset",
                    "daylight_duration", "sunshine_duration", "rain_sum",
                    "uv_index_max"
                ]
            }
            url = "https://api.open-meteo.com/v1/forecast"
            response = self.openmeteo.weather_api(url=url, params=params)[0]
            daily = response.Daily()

            daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
            daily_rain_sum = daily.Variables(2).ValuesAsNumpy()
            daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()
            daily_sunrise = daily.Variables(4).ValuesAsNumpy()
            daily_sunset = daily.Variables(5).ValuesAsNumpy()
            daily_daylight_duration = daily.Variables(6).ValuesAsNumpy()
            daily_sunshine_duration = daily.Variables(7).ValuesAsNumpy()
            daily_uv_index_max = daily.Variables(8).ValuesAsNumpy()

            times = pd.date_range(start=pd.to_datetime(daily.Time(),
                                                       unit="s",
                                                       utc=True),
                                  end=pd.to_datetime(daily.TimeEnd(),
                                                     unit="s",
                                                     utc=True),
                                  freq=pd.Timedelta(seconds=daily.Interval()),
                                  inclusive="left")

            daily_data = {
                "Date": times.astype(str),
                "Temperature Max(°C)": daily_temperature_2m_max,
                "Temperature Min(°C)": daily_temperature_2m_min,
                "Rain Sum(mm)": daily_rain_sum,
                "Wind Speed Max(m/s)": daily_wind_speed_10m_max,
                "Sunrise": daily_sunrise,
                "Sunset": daily_sunset,
                "Daylight Duration(H)": self.seconds_to_hours(daily_daylight_duration),
                "Sunshine Duration(H)": self.seconds_to_hours(daily_sunshine_duration),
                "UV Index Max": daily_uv_index_max
            }

            daily_dataframe = pd.DataFrame(data=daily_data)
            daily_dataframe = daily_dataframe.iloc[:7]  # Limit to 7 days
            return daily_dataframe
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})

    @profile
    def get_weekly_forecast(self, latitude: float,
                            longitude: float) -> pd.DataFrame:
        try:
            daily_df = self.get_daily_forecast(latitude, longitude)
            if "error" in daily_df.columns:
                return daily_df

            daily_df['date'] = pd.to_datetime(daily_df['date'])
            weekly_df = daily_df.resample('7D', on='date').agg({
                "temperature max":
                "mean",
                "temperature min":
                "mean",
                "rain sum":
                "sum",
                "wind speed":
                "max"
            }).reset_index()
            weekly_df['date'] = weekly_df['date'].astype(str)
            weekly_df = weekly_df.iloc[:2]  # Limit to 2 weeks
            return weekly_df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
