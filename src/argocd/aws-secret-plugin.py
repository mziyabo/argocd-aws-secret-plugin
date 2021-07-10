import boto3
import yaml
import re
import sys
import io


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
        if args[1] == "generate":
            template = io.open(args[2])

            generate(template.read())
