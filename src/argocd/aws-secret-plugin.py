import boto3
import yaml
import re
import sys
import io
import os


def generate(template: str):

    pattern = r"(\<.*?\>)"
    client = boto3.client('secretsmanager')

    try:
        yaml_templates = yaml.safe_load_all(template)

        for yaml_template in yaml_templates:
            matches = re.findall(pattern, str(yaml_template))

            for match in matches:
                res = client.get_secret_value(
                    SecretId=re.sub("[<>]", "", match))
                if res['SecretString']:
                    template = template.replace(
                        match, res['SecretString'])

        print(template)
    except client.exceptions.from_code("ResourceNotExistsError") as rne:
        raise rne
    except Exception as e:
        raise e


if __name__ == "__main__":
    args = sys.argv

    if len(args) == 3:
        path = args[2]
        if args[1] == "generate":
            if os.path.isfile(path):
                template = io.open(path)
                generate(template.read())
            else:
                for entry in os.scandir(path):
                    if entry.is_file():
                        if re.match(r"[a-zA-Z1-9\.\-_]*(yaml|yml)", entry.name):
                            template = io.open(os.path.join(path, entry.name))
                            generate(template.read())
