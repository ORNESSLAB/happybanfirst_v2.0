
Orness IBanFirst SDK
====================
Orness SDK allow you to develop application to process batch of payment with ibanfirst.


## requirement
java >= 8

run install.sh



## Authentication
username: 
```
from orness.ornessSDK import OrnessSDK

sdk = OrnessSDK()
sdk.login(username="user",password="password")
```

## Bulk Payments

file = "new_payments_v2.xlsx"
sdk.post_payment(file) --> return list of payments with status (awaintingcon) and ERRORs [list of payments, list of errors]



## Excel File
the template of the excel file is : new_payments_v2.xlsx


## TEST
cd myflask
python3 app.py





 

