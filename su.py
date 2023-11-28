import requests

url = "http://api.weatherapi.com/v1/current.json"

querystring = {"q": "12.33,76.61", "key": "5a0dcfb8b1a54edbaa015818230908"}

re = requests.get(url, params=querystring)
response=re.json()
print(response)
