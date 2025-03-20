
Orness IBanFirst SDK
====================
Orness SDK allow client to process batch payments with ibanfirst.
Assume you want to pay a list of suppliers at different time from different client wallet you own, the 
most simply way to do this is to fill an excel file with all information about the transaction you want to do and uppload it so that ornessSDK will 
parse the excel and send payments request to ibanfirst. 


## requirement
java >= 11 

To generate the swagger client we need java installed.

### setup ornessSDK

run install.sh 



## Authentication
username and password are provided by IBanFirst

```
from orness.ornessSDK import OrnessSDK

sdk = OrnessSDK()
sdk.login(username="user",password="password")
```

## Bulk Payments
```
file = "new_payments_v2.xlsx"
sdk.post_payment(file) # return list of payments with status (awaintingconfirmation, planified) and ERRORs [list of payments, list of errors]
```


## Excel File
the template of the excel file is : 
```
new_payments_v2.xlsx
```


## TEST
We make a POC with flask to test how to use the SDK

```
cd myflask
python3 app.py
```




 

