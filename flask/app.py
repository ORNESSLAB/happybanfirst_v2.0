import json
import re
from flask  import Flask, render_template, request, flash, redirect, url_for
import os
from orness import utils
from werkzeug.utils import secure_filename
import logging
import redis
rd = redis.Redis(host='localhost', port=6379, db=0)

extern = json.loads(rd.get('external_bank_accounts_info'))
pay_history = json.loads(rd.get('payments_histo'))

logger = logging.getLogger(__name__)

app = Flask(__name__)
@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])

def home():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if 'Se connecter' in request.form:
            conn = utils.authentication(user_id=username, password=password)
            app.logger.debug(f'{conn}:   Le test web')
            return redirect(url_for("operation"))

    else:
        return render_template("home.html", error="Invalid credentials")

@app.route("/operation", methods=["GET", "POST"])
def operation(user_id=None):
    user_id = os.getenv("IB_USERNAME")
    choice = request.form.get("choice")
    if choice == "submit_payment":
        return redirect(url_for("submit_payment"))
    if choice == "check_wallet":
        return redirect(url_for("check_wallet"))
    if choice == "create_bank_account":
        return redirect(url_for("create_account"))
    return render_template("choice.html", user_id=user_id)

def get_wallet():
    return render_template("check_wallet.html")

@app.route("/submit_payment", methods=["GET", "POST"])
def submit_payment():
    extern.insert(0, {'holderName': '--- Choisissez un compte ---'})
    data = {}
    if request.method == "POST":
        urgency = request.form.get("urgency")
        data['Priorité'] = ""
        if urgency == "Urgent":
            data['Priorité'] = "1H"
        if urgency == "Normal":
            data['Priorité'] = "24H"
        if urgency == "Différé":
            data['Priorité'] = "48H"
        recipient = request.form.get("recipient")
        if recipient == "--- Choisissez un compte ---":
            flash("Veuillez choisir un compte")
            data['Bénéficiaire']= ""
        else:
            data['Bénéficiaire']= recipient

        data['Compte Emetteur'] = request.form.get("source_account")
        data['Commentaire'] = request.form.get("comment")
        data['Libellé']= request.form.get("tag")
        data['Montant']= request.form.get("amount")
        
        data['Date désirée']= request.form.get("date")
        
        app.logger.debug(f'{data}:   ')
        result = utils.payload_dict(data=data)
        app.logger.debug(f'{result}:   ')
        
        
        return render_template("submit_payment.html", data=data, result=result, extern=extern)

    
    if request.method == "POST" and request.files:
        file = request.files["file"]
        if file.filename == "":
            flash("No file selected")
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            flash("File uploaded successfully")
            payload = utils.payload(file)
            app.logger.debug(f'the payload : {payload}:   ')
        

   
    return render_template('submit_payment.html', extern=extern, history=pay_history)

@app.route("/create_exteral_bank_account", methods=["GET", "POST"])
def create_account():
    return render_template("create_external.html")



if __name__ == "__main__":
    #print(f'{os.getenv("IB_PASSWORD")}')
    # t = ""
    # for i in extern:
    #     t = i["holderName"]
    #     break
    # print(t)

    #print(f'{i["holderName"]}' for i in extern)
    app.run(debug=True, port=8980)
