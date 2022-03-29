from flask import Flask

from api.OrdersApi import ordersApi
from api.StorageApi import storageApi

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.register_blueprint(storageApi, url_prefix='/storage')
app.register_blueprint(ordersApi, url_prefix='/orders')


@app.route('/')
def home():
    return 'Yeet'


app.run()
