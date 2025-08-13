from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.weatherapi import WeatherAPI
from pydantic import BaseModel
from time import time
from fastapi import Depends
from memory_profiler import profile
import os
from datetime import datetime


class WeatherRequest(BaseModel):
    city: str
    country: str = None
    period: str
    start_date: str


app = FastAPI()
weather_api = WeatherAPI()

static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

weather_cache = {}


@app.get("/")
def read_index() -> FileResponse:
    return FileResponse("static/index.html")


@profile
@app.get("/weather/")
def report_weather(request: WeatherRequest = Depends()) -> dict:
    cache_key = f"{request.city}_{request.country}_{request.period}"
    now = time()
    # 10 minutes cache
    if cache_key in weather_cache and now - weather_cache[cache_key][
            'time'] < 600:
        return weather_cache[cache_key]['data']
    try:
        lat, lon, _ = weather_api.get_lat_lon(request.city, request.country)
        weather_api.start_date = datetime.strptime(request.start_date, "%Y-%m-%d") if request.start_date else None
        print(request.start_date, type(request.start_date))
        print(weather_api.start_date, type(weather_api.start_date))

        if request.period == "hourly":
            df = weather_api.get_hourly_forecast(lat, lon)
        elif request.period == "daily":
            df = weather_api.get_daily_forecast(lat, lon)
        elif request.period == "weekly":
            df = weather_api.get_weekly_forecast(lat, lon)
        else:
            return {"error": ["Invalid period"]}
        # Ensure all columns are serializable
        for col in df.columns:
            if df[col].dtype == 'datetime64[ns]':
                df[col] = df[col].astype(str)
        result = df.to_dict(orient="list")
        weather_cache[cache_key] = {'data': result, 'time': now}
        return result
    except Exception as e:
        return {"error": [str(e)]}
