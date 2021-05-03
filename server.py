from flask import Flask, request, json
import requests
from flask_caching import Cache
from dotenv import dotenv_values

app = Flask(__name__)

cache = Cache()
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)
config = dotenv_values(".env")

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/currency', methods=['POST'])
def currnecy_convert():
    data = json.loads(request.data)
    fromCurrency = data["fromCurrency"]
    amount = data["amount"]
    toCurrency = data["toCurrency"]
    error = False
    result = None

    fromValueEUR = cache.get(fromCurrency) 
    toValueEUR =  cache.get(toCurrency) 

    API_KEY = config["API_KEY"]
    
    if fromValueEUR is None and toValueEUR is None:
        r = requests.get("http://data.fixer.io/api/latest?access_key=" + API_KEY + "&symbols=" + fromCurrency + "," + toCurrency)
        if r.json()["success"]:
            fromValueEUR = r.json()["rates"][fromCurrency]
            toValueEUR = r.json()["rates"][toCurrency]
            cache.set(fromCurrency, fromValueEUR, timeout=86400)
            cache.set(toCurrency, toValueEUR, timeout=86400)
        else: 
            error = True
    elif fromValueEUR is None: 
        r = requests.get("http://data.fixer.io/api/latest?access_key=" + API_KEY + "&symbols=" + fromCurrency)
        if r.json()["success"]:
            fromValueEUR = r.json()["rates"][fromCurrency]
            cache.set(fromCurrency, fromValueEUR, timeout=86400)
        else:
            error = True
    elif toValueEUR is None:
        r = requests.get("http://data.fixer.io/api/latest?access_key=" + API_KEY + "&symbols=" + toCurrency)
        if r.json()["success"]:
            fromValueEUR = r.json()["rates"][toValueEUR]
            cache.set(toCurrency, toValueEUR, timeout=86400)
        else:
            error = True
    else:
        print('all found in cache')

    if not error:
        convertedAmount = (amount / fromValueEUR) * toValueEUR

        result = {
            "amount": convertedAmount,
            "currency": toCurrency
        }, 200
    else:
        result = { error: 'please check the fixer api' }, 400
    return result