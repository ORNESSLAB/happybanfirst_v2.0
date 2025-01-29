import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def valid(json_file_dir:str, json_schema_file_dir:str):
    try:

        with open(json_file_dir) as f:
            doc = json.load(f)

        with open(json_schema_file_dir) as f:
            sch = json.load(f)

        try:
            validate(instance=doc, schema=sch)
            return 1
        except ValidationError as er:
            return 0

    except Exception as er:
        raise

if __name__ == '__main__':
    print(valid("orness/file/toto.json", "orness/file/wallet-schema.json"))
