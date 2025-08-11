from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from api.weatherapi import WeatherAPI
from pydantic import BaseModel


class WeatherRequest(BaseModel):
    city: str
    country: str = None
    period: str


app = FastAPI()
weather_api = WeatherAPI()

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.get("/")
def read_index():
    return FileResponse("static/index.html")


@app.post("/weather/")
def report_weather(request: WeatherRequest):
    try:
        lat, lon, _ = weather_api.get_lat_lon(request.city, request.country)
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
        return df.to_dict(orient="list")
    except Exception as e:
        return {"error": [str(e)]}
