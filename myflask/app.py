import json
import re
from flask  import Flask, render_template, request, flash, redirect, url_for, session
import os

from orness import ornessSDK
from werkzeug.utils import secure_filename
import logging
import redis
rd = redis.Redis(host='localhost', port=6379, db=0)
extern  = None
pay_history = None
wallets = None



logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "toto"
sdk = ornessSDK.OrnessSDK()

@app.route("/profile", methods=["GET", "POST"])
def profile():
    return 'Profile'


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session['username'] = request.form.get("client_id")
        session['password'] = request.form.get("password")

        if 'login' in request.form:
            sdk.login(username=session['username'], password=session['password'])
            app.logger.debug(f'Header:  {sdk.auth.header()}')
            global extern, pay_history, wallets
            assert isinstance(sdk.get_external_bank_account_info(), list), "Connexion Failed"
            extern = rd.set('external_bank_accounts_info', json.dumps(sdk.get_external_bank_account_info()))
            pay_history = rd.set('payments_histo', json.dumps(sdk.get_payments_status("all")['payments']))
            wallets = rd.set('wallets_info', json.dumps(sdk.get_wallets_holder_info()))
            
            return redirect(url_for("operation"))
            
    else:
        return render_template("login.html", error="Invalid credentials")
    
@app.route("/home", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/operation", methods=["GET", "POST"])
def operation(user_id=None):

    if "username" in session:
        extern = json.loads(rd.get('external_bank_accounts_info'))
        pay_history = list(reversed(json.loads(rd.get('payments_histo'))))
        pay_planified = list(reversed(json.loads(rd.get('payments_planified'))))
        wallets = json.loads(rd.get('wallets_info'))
        user_id = session['username']
        choice = request.form.get("choice")
        if choice == "submit_payment":
            return redirect(url_for("submit_payment"))
        if choice == "check_wallet":
            return redirect(url_for("check_wallet"))
        if choice == "create_bank_account":
            return redirect(url_for("create_account"))
        return render_template("choice.html", user_id=user_id)
    
    return redirect(url_for("login"))



@app.route("/submit_payment", methods=["GET", "POST"])
def submit_payment():
    
    data = {}
    len_extern = 0
    list_exteriban = ""
    if "username" in session:

        if request.method == "POST" and "file" in request.files:
            file = request.files["file"]
            if file.filename == "":
                
                return redirect(request.url)
            if file:
                filename = secure_filename(file.filename)
                payment, error = sdk.post_payment(filename)
                app.logger.debug(f'the payload : {payment}:   ')
                return render_template('payment_response.html',payment=payment, error_pay=error)

    
        if request.method == "POST":
            urgency = request.form.get("urgency")
            data['Priority'] = ""
            if urgency == "Urgent":
                data['Priority'] = "1H"
            if urgency == "Normal":
                data['Priority'] = "24H"
            if urgency == "Différé":
                data['Priority'] = "48H"



            data['Recipient']= request.form.get('ext_iban')

            data["Fees option"] = request.form.get('who_pay_fees')
            data['Comment'] = request.form.get("comment")
            data['Description']= request.form.get("tag")
            data['Amount']= request.form.get("amount")
            data['Sender'] = request.form.get("source_Id")
            data["Execution date"]= request.form.get("date")

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
    else:
        return redirect(url_for("login"))
    return render_template('submit_payment.html', extern=extern, len_extern=len_extern, wallets_list=wallets)


@app.route("/recipients", methods=["GET", "POST"])
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

        
        
        app.logger.debug(f"external: {data}")
        app.logger.debug(f"{result}:   ")
        return render_template("submit_payment.html", data=data)
        


    return render_template("recip.html", data=data)
@app.route("/history", methods=["GET", "POST"])
def history():

    return render_template("history.html", history=pay_history)


@app.route('/signup')
def signup():
    return 'Signup'

@app.route('/logout')
def logout():
    return 'Logout'

if __name__ == "__main__":
    #print(f"{os.getenv("IB_PASSWORD")}")
    # t = ""
    # for i in extern:
    #     t = i["holderName"]
    #     break
    # print(t)

    #print(f'{i["holderName"]}' for i in extern)
    
    app.run(debug=True, port=8980)
