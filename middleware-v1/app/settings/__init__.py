from typing import Any

import boto3
import json
import os
from pathlib import Path
from botocore.exceptions import ClientError
# Temporarily ignoring Kafka
# from kafka import KafkaProducer

region_name = os.getenv('REGION', 'ap-southeast-2')

# Create a Secrets Manager client
session = boto3.session.Session()
client = session.client(
    service_name='secretsmanager',
    region_name=region_name
)

def get_app_settings():
    settings = {
        'GENIE_BASE_URL': os.getenv('GENIE_BASE_URL', 'https://cass.ingest.littlebirdie.dev'),
        'LB_BASE_URL': os.getenv('LB_BASE_URL', "https://blue.littlebirdie.dev/"),
        'IMAGE_DEFAULT': os.getenv('IMAGE_DEFAULT',
                                   "https://littlebirdie.dev/static/media/no-image.300f547e81763cbc0bb4.jpg"),
        'SCRAPING_URL': os.getenv('SCRAPING_URL',
                                  "https://cass.ingest.littlebirdie.dev/v2/deal-scrape")
    }
    return settings


def get_secret(secret_name):
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = json.loads(get_secret_value_response['SecretString'])
    return secret


class SConfig:
    correlation_id = None
    MICRO_TAGS_BLACKLIST_DOMAINS_PATH = Path(__file__).resolve().parent / "microtag_blacklist_domains.json"

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SConfig, cls).__new__(cls,)
        return cls.instance

    def __init__(self):
        self.secrets = None
        self.webdb_secrets: dict = {}

    def secrets_manager(self) -> Any:
        run_env = os.getenv('RUN_ENV', None)
        if run_env and run_env == 'local':
            self.secrets = {'SERP_API_KEY': 'eab60650158ea34538da227aab07fed2df78b457a0781e798178822442cc523e'}
            return self.secrets

        if self.secrets is None:
            secret_name = os.getenv('SEARCH_SERVICE_SECRET_NAME', f"/{os.getenv('DEPLOY_ENV', 'uat')}/search-services")
            self.secrets = get_secret(secret_name)
        return self.secrets

    def init_webdb_secrets(self) -> None:
        if not self.webdb_secrets:
            webdb_secret_name = os.getenv('WEBDB_SECRET_NAME', f"/{os.getenv('DEPLOY_ENV', 'uat')}/webdb/postgres")
            self.webdb_secrets = get_secret(webdb_secret_name)

    @staticmethod
    def app_settings():
        return get_app_settings()

    # @staticmethod
    # def kafka_producer():
    #     kafka_servers = os.getenv('bootstrap_servers',
    #                               "b-3.lb-msk-uat-01.ixmnnk.c3.kafka.ap-southeast-2.amazonaws.com:9092,"
    #                               "b-2.lb-msk-uat-01.ixmnnk.c3.kafka.ap-southeast-2.amazonaws.com:9092,"
    #                               "b-1.lb-msk-uat-01.ixmnnk.c3.kafka.ap-southeast-2.amazonaws.com:9092")
    #     producer = KafkaProducer(
    #         bootstrap_servers=kafka_servers,
    #         value_serializer=lambda m: json.dumps(m).encode('ascii'),
    #         api_version=(0, 10, 1))
    #     return producer

    @staticmethod
    def sqs_client():
        return boto3.client('sqs', region_name=region_name)
