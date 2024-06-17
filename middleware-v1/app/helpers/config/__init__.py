import os
import logging


class Config:
    GENIE_PRICE_HISTORY_ENDPOINT = "/offer/price_history?id={offer_id}"

    @staticmethod
    def get_environment() -> str:
        env = os.getenv('RUN_ENV')
        if env == "lambda":
            return env
        else:
            return 'local'

    def is_lambda(self) -> bool:
        if self.get_environment() == "lambda":
            return True
        else:
            return False
