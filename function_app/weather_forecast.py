import logging
import azure.functions as func
import json
from urllib.request import urlopen
from typing import List


app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    weather_object = None
    response = urlopen('http://api.openweathermap.org/data/2.5/weather?q=Seoul,kr&exclude=hourly&APPID=<API_key>')

    if response.getcode() == 200:
        result = json.loads(response.read())
        weather_object = result
    else:
        return func.HttpResponse('Problem!!!!!', status_code=400)

    weather_advice = get_weather_advice(weather_object)
    return func.HttpResponse(weather_advice)

def get_weather_advice(weather_object):
    if weather_object is None or 'main' not in weather_object:
        return 'Just wear something'

    main_info = weather_object['main']
    feels_like_temp = main_info['feels_like'] - 273.15 # Kelvin to Celsius
    if feels_like_temp >= 30.0:
        return "It's summer"
    elif feels_like_temp >= 20.0:
        return "It's sunny"
    elif feels_like_temp >= 10.0:
        return "It's cool"
    elif feels_like_temp >= 0.0:
        return "It's cold"
    else:
        return "It's freezing"
