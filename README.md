# Weather API

A simple FastAPI application that provides weather forecasts (hourly, daily, weekly) for any city using the Open-Meteo API.  
Includes a web frontend for easy access and visualization.

---

## Features

- Get weather forecasts by city and country
- Hourly (24h), daily (7d), and weekly (2w) forecast options
- FastAPI backend with caching for performance
- Responsive HTML frontend with clean table output
- Docker support for easy deployment

---

## Getting Started

### Requirements

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- [Docker](https://www.docker.com/) (optional, for containerized deployment)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/weather-api.git
    cd weather-api
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Run the application:**
    ```sh
    fastapi run main.py
    ```
    The app will be available at [http://localhost:8000](http://localhost:8000).

---

## Usage

1. Open [http://localhost:8000](http://localhost:8000) in your browser.
2. Enter a city (and optionally a country).
3. Select the forecast period (24 Hours, 7 Days, 2 Weeks).
4. Click "Get Weather" to view the forecast in a table.

---

## API

### POST `/weather/`

**Request JSON:**
```json
{
  "city": "London",
  "country": "GB",
  "period": "hourly" // or "daily" or "weekly"
}
```

**Response:**
- On success: JSON object with columns as keys and lists as values.
- On error: `{ "error": ["Error message"] }`

---

## Docker

See [README.Docker.md](README.Docker.md) for Docker usage instructions.

---

## Credits

- [Open-Meteo API](https://open-meteo.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pandas](https://pandas.pydata.org/)

---