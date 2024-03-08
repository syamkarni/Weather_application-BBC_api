from flask import Flask, render_template, request
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re
import pandas as pd

app = Flask(__name__)

def get_location_id(city):
    city = city.lower()
    location_url = 'https://locator-service.api.bbci.co.uk/locations?' + urlencode({
        'api_key': 'AGbFAKx58hyjQScCXIYrxuEwJh2W2cmv',
        's': city,
        'stack': 'aws',
        'locale': 'en',
        'filter': 'international',
        'place-types': 'settlement,airport,district',
        'a': 'true',
        'format': 'json'
    })
    result = requests.get(location_url).json()
    location = result['response']['results']['results'][0]['id']
    return location

def scrape_weather(city):
    location_id = get_location_id(city)
    url = 'https://www.bbc.com/weather/' + location_id
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    daily_high_values = soup.find_all('span', attrs={'class': 'wr-day-temperature__high-value'})
    daily_low_values = soup.find_all('span', attrs={'class': 'wr-day-temperature__low-value'})
    daily_summary = soup.find('div', attrs={'class': 'wr-day-summary'}).text.strip()

    daily_summary_list = re.findall('[a-zA-Z][^A-Z]*', daily_summary)

    datelist = pd.date_range(pd.Timestamp.today(), periods=len(daily_high_values)).tolist()

    weather_data = []
    #for i in range(len(datelist)):
    for i in range(12):
        weather_data.append({
            'name': str(city).capitalize(),
            'date': str(datelist[i].strftime('%d-%m-%Y')),
            'high': daily_high_values[i].text.strip(),
            'low': daily_low_values[i].text.strip(),
            'summary': daily_summary_list[i]
        })

    return weather_data

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            weather_data = scrape_weather(city)
    return render_template('index.html', weather_data=weather_data)

if __name__ == '__main__':
    app.run(debug=True)
