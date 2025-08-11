import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry


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

    def get_hourly_forecast(self, latitude: float,
                            longitude: float) -> pd.DataFrame:
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": ["temperature_2m", "rain", "wind_speed_10m"]
            }
            url = "https://api.open-meteo.com/v1/forecast"
            response = self.openmeteo.weather_api(url=url, params=params)[0]
            hourly = response.Hourly()

            hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
            hourly_rain = hourly.Variables(1).ValuesAsNumpy()
            hourly_wind_speed_10m = hourly.Variables(2).ValuesAsNumpy()

            times = pd.date_range(start=pd.to_datetime(hourly.Time(),
                                                       unit="s",
                                                       utc=True),
                                  end=pd.to_datetime(hourly.TimeEnd(),
                                                     unit="s",
                                                     utc=True),
                                  freq=pd.Timedelta(seconds=hourly.Interval()),
                                  inclusive="left")

            hourly_data = {
                "date": times.astype(str),
                "temperature_2m": hourly_temperature_2m,
                "rain": hourly_rain,
                "wind_speed_10m": hourly_wind_speed_10m
            }

            hourly_dataframe = pd.DataFrame(data=hourly_data)
            hourly_dataframe = hourly_dataframe.iloc[:24]  # Limit to 24 hours
            return hourly_dataframe
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})

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
                    "wind_speed_10m_max"
                ]
            }
            url = "https://api.open-meteo.com/v1/forecast"
            response = self.openmeteo.weather_api(url=url, params=params)[0]
            daily = response.Daily()

            daily_temperature_2m_max = daily.Variables(0).ValuesAsNumpy()
            daily_temperature_2m_min = daily.Variables(1).ValuesAsNumpy()
            daily_rain_sum = daily.Variables(2).ValuesAsNumpy()
            daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()

            times = pd.date_range(start=pd.to_datetime(daily.Time(),
                                                       unit="s",
                                                       utc=True),
                                  end=pd.to_datetime(daily.TimeEnd(),
                                                     unit="s",
                                                     utc=True),
                                  freq=pd.Timedelta(seconds=daily.Interval()),
                                  inclusive="left")

            daily_data = {
                "date": times.astype(str),
                "temperature_2m_max": daily_temperature_2m_max,
                "temperature_2m_min": daily_temperature_2m_min,
                "rain_sum": daily_rain_sum,
                "wind_speed_10m_max": daily_wind_speed_10m_max
            }

            daily_dataframe = pd.DataFrame(data=daily_data)
            daily_dataframe = daily_dataframe.iloc[:7]  # Limit to 7 days
            return daily_dataframe
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})

    def get_weekly_forecast(self, latitude: float,
                            longitude: float) -> pd.DataFrame:
        try:
            daily_df = self.get_daily_forecast(latitude, longitude)
            if "error" in daily_df.columns:
                return daily_df

            daily_df['date'] = pd.to_datetime(daily_df['date'])
            weekly_df = daily_df.resample('7D', on='date').agg({
                "temperature_2m_max":
                "mean",
                "temperature_2m_min":
                "mean",
                "rain_sum":
                "sum",
                "wind_speed_10m_max":
                "max"
            }).reset_index()
            weekly_df['date'] = weekly_df['date'].astype(str)
            weekly_df = weekly_df.iloc[:2]  # Limit to 2 weeks
            return weekly_df
        except Exception as e:
            return pd.DataFrame({"error": [str(e)]})
