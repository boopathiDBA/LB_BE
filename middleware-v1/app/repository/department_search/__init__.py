import os
import re
import json
import requests
import marshmallow_dataclass
from jinja2 import Template
from typing import List, Any, Union

from app.repository import IOffer, SearchOffersInput
from app.model.entities import Offer, OfferAttributes
from app.settings import SConfig
from app.helpers.log import logger
from app.repository.helpers import Support


class DepartmentSearch(IOffer):

    def __init__(
            self, sconfig: SConfig
    ) -> None:
        self.secrets = sconfig.secrets_manager()

    def search_by_link(self, link: str, wildcard_search: bool = True) -> Offer:
        data = self.__get_department(link, self.secrets, self)
        try:
            data = json.loads(data)['hits']['hits']
        except Exception as e:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             error=e, object=json.loads(data),
                             message="Error occurred in DepartmentSearch by link"))

        return data

    def get_offer_info(self, search_input: SearchOffersInput) -> Offer:
        pass

    def search_by_links(self, google_offers: List[Offer], offer: Offer) -> Offer:
        pass

    def search_by_title(self, title: str) -> List[Offer]:
        pass

    def search_attributes_by_id(self, id: str) -> Union[OfferAttributes, bool]:
        pass

    @staticmethod
    def __get_department(link: str, secrets: dict, self) -> Any:
        # Open search variables
        open_search_host = os.getenv('OPENSEARCH_HOST', 'https://search.stream.littlebirdie.dev')
        client_index = os.getenv('OPENSEARCH_INDEX', 'a_deals')
        # TODO: This URL has to be changed when PD team will provide exact information
        open_search_url = f"{open_search_host}/{client_index}/_search/template"
        headers = {'Content-type': 'application/json'}
        logger.info(f"Search Link: {link}")

        # Using jinja2 to prepare template for Opensearch
        template = self.__search_template()
        aquery = template.render(to_search=link)
        logger.info(f"Jinja2 Template: {aquery}")

        try:
            logger.info(dict(correlation_id=SConfig.correlation_id,
                             message="Department OpenSearch API Execution Started",
                             url=open_search_url, data=aquery, headers=headers))
            document = requests.get(url=open_search_url, data=aquery, headers=headers)
            output = document.json()

            body = json.dumps(output, separators=(',', ':'))
        except Exception as err:
            body = f"Error fetching data from OpenSearch with message:{err}"
            logger.info(body)

        return body

    @staticmethod
    def __search_template() -> Template:
        # Preparing jinja Template object here
        template = Template('''
        {
            "id":"browser_extension_search",
             "params": {
                "query_string": "{{to_search}}",
                "from": 0,
                "size": 40
             }
        }
        ''')
        return template
