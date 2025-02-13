
#! /usr/bin/bash
#create a python virtual env

/bin/python3 -m venv ibanvenv
source ibanvenv/bin/activate

echo "Download swagger codegen jar" 
/usr/bin/wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.66/swagger-codegen-cli-3.0.66.jar -O swagger-codegen-cli.jar
echo "Download the ClientAPI swagger "
#/usr/bin/wget https://docs.ibanfirst.com/apis/clientapi/ClientAPI.yaml -P /var/tmp/
cp swagger.yaml /var/tmp/ClientAPI.yaml
echo "Generate ibanfirst client api"
java -jar swagger-codegen-cli.jar generate -i /var/tmp/ClientAPI.yaml -l python
echo "change swagger-client to ibanfirst_client in entire project"
mv swagger_client ibanfirst_client
sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*.py
sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*/*.py
sed -i 's/swagger_client/ibanfirst_client/g' test/*.py
sed -i 's/swagger-client/Orness_client/g' setup.py
echo -e 'python-dotenv\njsonschema\npandas == 2.2.3\nopenpyxl\ncountry-converter\nconfigparser\npyyaml' >> requirements.txt
touch .env 
echo -e "IB_USERNAME= \nIB_PASSWORD= \nIB_HOST= \nLOG_FILE= \nSETTINGS_FILE=" > .env
echo "install required modules"
pip install -r requirements.txt
echo "set up the client api"
python setup.py install
