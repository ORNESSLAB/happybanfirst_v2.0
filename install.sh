#! /usr/bin/bash
#
OSNAME="$(grep -E '^NAME=' /etc/os-release | cut -c6- | sed 's/\"//g')"
INSTALLCMD=
if [ "$OSNAME" = "Ubuntu" ]
then
	echo "$OSNAME"
	INSTALLCMD='apt'
else
	echo "pas ubuntu"
fi
#create a python virtual env

/bin/python3 -m venv ibanvenv
cd ibanvenv
source bin/activate

echo "Download swagger codegen jar" 
/usr/bin/wget https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.66/swagger-codegen-cli-3.0.66.jar -O swagger-codegen-cli.jar

echo "Generate ibanfirst client api"
java -jar swagger-codegen-cli.jar generate -i happybanfirst_v2.0/swagger.yaml -l python -o ibandir
cd ibandir
echo "change swagger-client to ibanfirst_client in entire project"
mv swagger_client ibanfirst_client
sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*.py
sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*/*.py
sed -i 's/swagger-client/ibanfirst-client/g' setup.py
echo "install required modules"
pip install -r requirements.txt
echo "set up the client api"
python setup.py install

