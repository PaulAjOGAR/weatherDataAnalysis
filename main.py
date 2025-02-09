from datetime import datetime, timedelta

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

WEATHERAPI_KEY = "c7a754bf38384796ad2214825250802"


def fetch_weather_data(city, start_date, end_date, api_key=WEATHERAPI_KEY):
    records = []
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        url = f"https://api.weatherapi.com/v1/history.json?key={api_key}&q={city}&dt={date_str}"

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()

            if "forecast" not in data or "forecastday" not in data["forecast"]:
                print(f"No data for {date_str}")
                current_date += timedelta(days=1)
                continue

            for hour in data["forecast"]["forecastday"][0]["hour"]:
                records.append({
                    "datetime": hour["time"],
                    "temperature": hour["temp_c"],
                    "humidity": hour["humidity"],
                    "pressure": hour["pressure_mb"],
                    "weather": hour["condition"]["text"]
                })

        else:
            print(f"Error fetching data for {date_str}: {response.text}")

        current_date += timedelta(days=1)

    return records if records else None


@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city', 'London')
    year = request.args.get('year', '2023')

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    data = fetch_weather_data(city, start_date, end_date)

    if data:
        return jsonify({"city": city, "year": year, "data": data})
    else:
        return jsonify({"error": "No data found"}), 404


if __name__ == '__main__':
    app.run(debug=True)
