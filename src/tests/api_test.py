import sys
import os

sys.path.insert(0,
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest

from api.weatherapi import WeatherAPI


class WeatherAPITest(unittest.TestCase):

    def setUp(self):
        self.weather_api = WeatherAPI()

    def test_get_lat_lon(self):
        lat, lon, country = self.weather_api.get_lat_lon("Berlin", "Germany")
        self.assertEqual(type(lat), float)
        self.assertEqual(type(lon), float)
        self.assertEqual(type(country), str)

    def test_get_hourly_forecast(self):
        df = self.weather_api.get_hourly_forecast(52.52437, 13.41053)
        self.assertEqual(type(df.shape[0]), int)

    def test_get_daily_forecast(self):
        df = self.weather_api.get_daily_forecast(52.52437, 13.41053)
        self.assertEqual(type(df.shape[0]), int)


if __name__ == "__main__":
    unittest.main()
