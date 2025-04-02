
#! /usr/bin/bash


function install {
    SWAGGER_YAML="../swagger.yaml"
    CODEGEN_JAR="swagger-codegen-cli.jar"
    CODEGEN_URL="https://repo1.maven.org/maven2/io/swagger/codegen/v3/swagger-codegen-cli/3.0.66/swagger-codegen-cli-3.0.66.jar"
    mkdir src
    cd src
    echo "Download swagger codegen jar" 
    wget "$CODEGEN_URL"  -O "$CODEGEN_JAR"
    echo "Download the ClientAPI swagger "
    #/usr/bin/wget https://docs.ibanfirst.com/apis/clientapi/ClientAPI.yaml -P /var/tmp/

    echo "Generate ibanfirst client api"
    java -jar "$CODEGEN_JAR" generate -i  "$SWAGGER_YAML" -l python
    echo "change swagger-client to ibanfirst_client in entire project"
    mv swagger_client ibanfirst_client
    sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*.py
    sed -i 's/swagger_client/ibanfirst_client/g' ibanfirst_client/*/*.py
    sed -i 's/swagger_client/ibanfirst_client/g' test/*.py
    #sed -i 's/swagger-client/Orness_client/g' setup.py
    cd ..
    
    
}

#-------------------------------------------------

install
poetry --version
poetry add $(cat requirements.txt)
poetry lock --no-interaction
poetry install --no-interaction
poetry build
#-------------------------------------------------
