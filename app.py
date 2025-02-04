from flask import request, jsonify, Flask, request, flash, redirect, url_for
from flask_restful import Resource
from flask_restful import Api
import os
from werkzeug.utils import secure_filename
from orness.orness_api import IbWalletApi
import pandas as pd
import json

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = ''
ALLOWED_EXTENSIONS = {'json', 'csv', 'xlsx', 'xls'}

@app.route("/", methods=["GET"])
def hello():
    return "{'status': 'success'}"
@app.route("/test", methods=["POST", "GET"])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('hello', filename=''))
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return set_url(filename)
            #return redirect(url_for('hello',filename=filename))
    return '''
    <!doctype html>
    <title>Payment</title>
    <h1> new payment</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''
    
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def set_url_param(filemane):
    myjson = {}
    if 'json' in filemane.lower():
        with open(filemane, 'r') as f:
            myjson = json.load(f) 
    if 'csv' in filemane.lower():
        with open(filemane, 'r') as f:
            csvfile = pd.read_csv(filemane)
            myjson = csvfile.to_json(orient='records')

    if 'xls' or 'xlsx' in filemane.lower():
        with open(filemane, 'r') as f:
            exc = pd.read_excel(filemane)
            myjson = exc.to_json(orient='records')
    return convert_json_url_param(myjson)

def convert_json_url_param(data):
    """
    Convert data to be pushed in endpoint

    Args:
        data (_dict_): dict 

    Returns:
        _type_: _description_
    """
    url_param= ""
    while len(data) != 0:
        for key, value in data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    url_param += f"{key}[{k}]={v}&"
            else:     
                url_param += f"{key}={value}&" 
            data.pop(key)
            break
    
    return url_param[:-1]

@app.route('/wallets/', methods=["GET"])
def get_wallets():
    wallets = IbWalletApi()
    return wallets.wallets_get().json()

@app.route('/wallets/<id>/', methods=["GET"])
def get_wallet(id):
    wallet = IbWalletApi()
    return wallet.wallets_id_get(id).json()

@app.route('/payments/<id>/', methods=["GET"])
def pay(id):
    
    return redirect(url_for('get_wallet', id=id))

if __name__ == "__main__":
    #app.run(debug=True, port=8980)
    print(set_url_param('submit_payment.json'))