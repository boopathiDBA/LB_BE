from app.repository.web_affiliate import WebAffiliate


class MockWebAffiliate(WebAffiliate):
    def __init__(self) -> None:
        super().__init__()

    def _check_affiliate_status(self, tld, domain):
        pass
