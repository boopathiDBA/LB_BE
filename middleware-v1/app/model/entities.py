from dataclasses import dataclass, field
from typing import List
from urllib.parse import urlparse, urljoin
from app.settings import SConfig
from marshmallow import Schema, fields

import marshmallow


@dataclass
class Offer:
    # field metadata is used to instantiate the marshmallow field
    id: int = field(default=0)
    title: str = field(default="anonymous-title", metadata=dict(required=True))
    description: str = field(default="anonymous-description")
    # link is being used to affiliate url in WebOffer repository
    link: str = field(default="anonymous-link")
    # TODO: - external link omit from sending in API response, not part of it
    # slug is normalised link to uniquely identify an offer from a merchant
    slug: str = field(default="anonymous-slug")
    # offer_url purpose is to redirect to product page or affiliate_url is required
    offer_url: str = field(default="anonymous-url", metadata=dict(marshmallow_field=marshmallow.fields.Url()))

    image_url: str = field(default=None)
    store_name: str = field(default="anonymous-link")
    price: float = field(default=0.0)
    in_stock: bool = field(default="anonymous-link")
    confidence: str = field(default="low")
    searched: bool = field(default=False)
    source: str = field(default="gs")
    ops_score: float = field(default=0.0, metadata=dict(required=False))
    text_score: float = field(default=0.0, metadata=dict(required=False))
    product_code_score: float = field(default=0.0, metadata=dict(required=False))
    attrs_score: float = field(default=0.0, metadata=dict(required=False))
    brand_score: float = field(default=0.0, metadata=dict(required=False))
    image_score: float = field(default=0.0, metadata=dict(required=False))
    savings: float = field(default=0.0, metadata=dict(required=False))
    product_id: int = field(default=None, metadata=dict(required=False, product_identifier=True))
    is_only_img_match: bool = field(default=False, metadata=dict(required=False))
    # Todo : remove these old fields
    # openai_attributes: list = field(default=None, metadata=dict(required=False))
    # google_pid: str = field(default=None, metadata=dict(required=False))
    department_name: str = field(default="", metadata=dict(required=False))
    category_name: str = field(default=None, metadata=dict(required=False))
    subcategory_name: str = field(default=None, metadata=dict(required=False))
    af: bool = field(default=False)
    source_id: str = field(default=None, metadata=dict(required=False))
    vendor_id: str = field(default=None, metadata=dict(required=False))
    origin_store_id: str = field(default=None, metadata=dict(required=False))
    xpath_obj: dict = field(default=None, metadata=dict(required=False))
    # New fields for BE-950
    gtin: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    mpn: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    upc: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    isbn: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    ean: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    asin: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    gpid: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    attrs: dict = field(default=None, metadata=dict(required=False))
    pos_attrs: dict = field(default=None, metadata=dict(required=False))
    neg_attrs: dict = field(default=None, metadata=dict(required=False))
    brand: str = field(default=None, metadata=dict(required=False))
    brand_name: str = field(default=None, metadata=dict(required=False))
    product_codes: list = field(default_factory=list, metadata=dict(required=False))
    expiry_date: str = field(default=None, metadata=dict(required=False))
    url_match: bool = field(default=True, metadata=dict(required=False))

    def __post_init__(self):
        slug = f"{urlparse(self.offer_url).netloc}{urlparse(self.offer_url).path}".strip("www.")
        self.slug: str = slug.lower()
        if not self.image_url:
            self.image_url: str = SConfig().app_settings().get("IMAGE_DEFAULT")


class OfferAPISchema(Schema):
    id = fields.Str()
    title = fields.Str()
    offer_url = fields.Str()
    image_url = fields.Str()
    store_name = fields.Str()
    price = fields.Float()
    in_stock = fields.Bool()
    confidence = fields.Str()
    searched = fields.Bool()
    source = fields.Str()
    ops_score = fields.Float()
    savings = fields.Float()
    product_id = fields.Int()
    vendor_id = fields.Str()
    origin_store_id = fields.Str()
    source_id = fields.Str()
    xpath_obj = fields.Dict()

@dataclass
class OfferAttributes:
    id: int = field(default=0)
    title: str = field(default="anonymous-title", metadata=dict(required=True))
    product_id: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    # Todo : remove these old fields
    # raw_brand_name: str = field(default=None, metadata=dict(required=False))
    # raw_size: str = field(default=None, metadata=dict(required=False))
    # raw_color: str = field(default=None, metadata=dict(required=False))
    # openai_attributes: list = field(default=None, metadata=dict(required=False))
    # google_pid: str = field(default=None, metadata=dict(required=False))
    department_name: str = field(default="", metadata=dict(required=False))
    category_name: str = field(default=None, metadata=dict(required=False))
    subcategory_name: str = field(default=None, metadata=dict(required=False))
    viewing_url: str = field(default=None)
    # New fields for BE-950
    gtin: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    mpn: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    upc: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    isbn: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    ean: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    asin: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    gpid: str = field(default=None, metadata=dict(required=False, product_identifier=True))
    attrs: dict = field(default=None, metadata=dict(required=False))
    pos_attrs: dict = field(default=None, metadata=dict(required=False))
    neg_attrs: dict = field(default=None, metadata=dict(required=False))
    brand: str = field(default=None, metadata=dict(required=False))
    brand_name: str = field(default=None, metadata=dict(required=False))
    product_codes: list = field(default_factory=list, metadata=dict(required=False))
    expiry_date: str = field(default=None, metadata=dict(required=False))


@dataclass
class Extras:
    price_alert: bool = field(default=False)
    savings: float = field(default=None)
    product: str = field(default=None)


@dataclass
class ResponseWithExtras:
    offers: List[OfferAPISchema]
    extras: dict


@dataclass
class SuccessResponse:
    data: ResponseWithExtras


@dataclass
class MockSuccessResponse:
    data: ResponseWithExtras
