import os
from flask import Flask, send_from_directory
from flask_cors import CORS
from src.api.OrdersApi import ordersApi
from src.api.StaffApi import staffApi
from src.api.StorageApi import storageApi

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['JSON_AS_ASCII'] = False

app.register_blueprint(storageApi, url_prefix='/storage')
app.register_blueprint(ordersApi, url_prefix='/orders')
app.register_blueprint(staffApi, url_prefix='/staff')


@app.route('/')
def home():
    return 'Yeet'


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, '../static'), 'favicon.ico')


app.run()
