from flask import Flask, request, json
import requests
from flask_caching import Cache

app = Flask(__name__)

cache = Cache()
app.config['CACHE_TYPE'] = 'simple'
cache.init_app(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/currency', methods=['POST'])
@cache.cached(timeout=86400)
def currnecy_convert():
    data = json.loads(request.data)
    fromCurrency = data["fromCurrency"]
    amount = data["amount"]
    toCurrency = data["toCurrency"]

    fromValueEUR = cache.get(fromCurrency) 
    toValueEUR =  cache.get(toCurrency) 

    API_KEY = "2e70aaac34352ee4b4d69286fb7064c0"
    
    if fromValueEUR is None and toValueEUR is None:
        r = requests.get("http://data.fixer.io/api/latest?access_key=b08103793b70e9d70684b581c1fd31ea&symbols=" + fromCurrency + "," + toCurrency)
        fromValueEUR = r.json()["rates"][fromCurrency]
        toValueEUR = r.json()["rates"][toCurrency]
    elif fromValueEUR is None: 
        r = requests.get("http://data.fixer.io/api/latest?access_key=b08103793b70e9d70684b581c1fd31ea&symbols=" + fromCurrency)
        fromValueEUR = r.json()["rates"][fromCurrency]
    elif toValueEUR is None:
        r = requests.get("http://data.fixer.io/api/latest?access_key=b08103793b70e9d70684b581c1fd31ea&symbols=" + toCurrency)
        fromValueEUR = r.json()["rates"][toValueEUR]
    else:
        print('all found in cache')

    convertedAmount = (amount / fromValueEUR) * toValueEUR

    result = {
        "amount": convertedAmount,
	    "currency": toCurrency
    }

    return result