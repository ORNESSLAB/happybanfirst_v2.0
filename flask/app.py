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
pay_history = list(reversed(json.loads(rd.get('payments_histo'))))
pay_planified = list(reversed(json.loads(rd.get('payments_planified'))))

wallets = json.loads(rd.get('wallets_info'))


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
    
    data = {}
    len_extern = 0
    list_exteriban = ""
    if request.method == "POST" and "file" in request.files:
        file = request.files["file"]
        if file.filename == "":
            
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            payment = utils.post_payment(filename)
            app.logger.debug(f'the payload : {payment}:   ')
            return render_template('submit_payment.html', extern=extern, list_extern = list_exteriban, history=pay_history, wallets_list=wallets, plan=pay_planified, payment=payment)
    
    if request.method == "POST" and "add_recipient" in request.form:
        recipient = request.form.get("recipient")
        list_exteriban = utils.get_external_iban_with_same_name(name=recipient)
        app.logger.debug(list_exteriban)
    
        return render_template('submit_payment.html', data=data, extern=extern, list_extern = list_exteriban, history=pay_history, wallets_list=wallets, plan=pay_planified)
    
    
    if request.method == "POST":
        urgency = request.form.get("urgency")
        data['Urgence'] = ""
        if urgency == "Urgent":
            data['Urgence'] = "1H"
        if urgency == "Normal":
            data['Urgence'] = "24H"
        if urgency == "Différé":
            data['Urgence'] = "48H"
        
        
        
        data['Bénéficiaire']= request.form.get('ext_iban')

        data["Détails des frais"] = request.form.get('who_pay_fees')
        data['Commentaire'] = request.form.get("comment")
        data['Libellé']= request.form.get("tag")
        data['Montant']= request.form.get("amount")
        data['Expéditeur'] = request.form.get("source_Id")
        data["Date d’exécution"]= request.form.get("date")
        
        app.logger.debug(f'{data}:   ')
        result = utils.post_payment_from_form(form_data=data)
        typo = ""
        if isinstance(result, int):
            typo = "int" 
        if isinstance(result, dict):
            typo = "dict"
            if 'rate' not in result['payment'].keys():
                result['payment']['rate'] = {'currencyPair': 'None', 
                                             'midMarket': None, 'date': None, 
                                             'coreAsk': None, 'coreBid': None, 
                                             'appliedAsk': None, 'appliedBid': 'inconnu'}
            if 'counterValue' not in result['payment'].keys():
                result['payment']['counterValue'] = {'value': 'wait', 'currency': 'wait'}
            pay_history.insert(0,result['payment'])
        

        app.logger.debug(f'{result}:   ')
        
        
        return render_template("submit_payment.html", data=data, result=result, extern=extern, list_extern = list_exteriban, typo=typo, history=pay_history, wallets_list=wallets, plan=pay_planified)

   
    return render_template('submit_payment.html', extern=extern, history=pay_history, len_extern=len_extern, wallets_list=wallets, plan=pay_planified)

@app.route("/create_exteral_bank_account", methods=["GET", "POST"])
def create_account():
    data = {}
    data['holder'] = {}
    data['holderBank'] = {}
    data["holderBank"]["address"] = {}
    data["holder"]["address"] = {}
    if request.method == "POST":
        data["currency"] = request.form.get("currency")
        data["accountNumber"] = request.form.get("iban")
        data["tag"] = request.form.get("tag")
        data["correspondentBankBic"] = request.form.get("correspondentBank")

        data["holder"]["name"] = request.form.get("holderName")
        data["holder"]["address"]["street"] =  request.form.get("holderStreet")
        data["holder"]["address"]["postCode"] = request.form.get("holderPostalCode")
        data["holder"]["address"]["city"] = request.form.get("holderCity")
        data["holder"]["address"]["country"] = request.form.get("holderCountry")
        data["holder"]["type"] = request.form.get("holderType")

        data["holderBank"]["address"]["street"]= request.form.get("bankStreet")
        data["holderBank"]["address"]["postCode"] = request.form.get("bankPostalCode")
        data["holderBank"]["address"]["city"] = request.form.get("bankCity")
        data["holderBank"]["address"]["country"] = request.form.get("bankCountry")
        data["holderBank"]["address"]["state"]= request.form.get("bankState")
        data["holderBank"]["bic"] = request.form.get("bic")
        data["holderBank"]["name"] = request.form.get("bankName")
        data["holderBank"]["clearingCodeType"] = request.form.get("clearingCodeType")
        data["holderBank"]["clearingCode"] = request.form.get("clearingCode")

        result = 0 #utils.create_beneficiary(data)
        
        app.logger.debug(f"external: {data}")
        app.logger.debug(f"{result}:   ")
        return render_template("submit_payment.html", data=data, result=result)
        


    return render_template("create_external.html", data=data)



if __name__ == "__main__":
    #print(f"{os.getenv("IB_PASSWORD")}")
    # t = ""
    # for i in extern:
    #     t = i["holderName"]
    #     break
    # print(t)

    #print(f'{i["holderName"]}' for i in extern)
    
    app.run(debug=True, port=8980)
