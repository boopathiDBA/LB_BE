from app.repository.helpers import Support
from app.model.entities import Offer
from app.helpers.log import logger
from app.settings import SConfig
from typing import Tuple, List, Dict


class CalculateScore:
    def __init__(self, apply_threshold: bool):
        self.offer_attrs = None
        self.confidence_threshold = 0.95
        self.min_lb_threshold = 0.6
        self.gs_threshold = 0.95
        self.apply_threshold = apply_threshold
        self.support = Support()
        self.top_match_stores = list()

    # ToDo: Define "offer_attrs" as a Class instead of Dict
    def calculate_confidence(self, offer_attrs: Dict, offers: List[Offer]) -> List[Offer]:
        """
                Action : Method to calcuate confidence score for each offers using input offer_attrs
                Conditions :
                1.Looping through all the offers
                2.Calculate title match score against input offer
                3.Calculate product code match score (gtin,asin,upc,isbn,ean) score against input offer
                4.Calculate attrs score against input when score < threshold
                5.Calculate brand match score against input when score < threshold
        """
        offer_processed = []
        # ToDo: refactor this to send offer_attrs directly to the method instead of using the object itself
        self.offer_attrs = offer_attrs
        input_title = self.support.clean_text(self.offer_attrs.get("title"))
        brand = self.support.clean_text(str(self.offer_attrs.get("brand") or ''))
        input_title = f"{brand} {input_title}" if brand not in input_title else input_title
        message = []
        for each_offer in offers:
            text_score = 0.0
            attrs_score = 0.0
            product_code_score = 0.0
            brand_score = 0.0
            total_score = 0.0
            has_brand_match = False
            # if each_offer.id == 1249633875:
            # print("yay")
            name = self.support.clean_text(each_offer.title)
            has_brand_match = self.__is_brand_match(each_offer)
            # Rule 1 : calculate text score
            text_score = self.support.get_cosine(input_title, name)
            total_score = text_score
            # Rule 2 : calculate product code score(gtin,mpn,upc,isbn,ean,gpid,product_id)
            product_code_score, overwrite = self.get_product_code_match_score(each_offer, total_score, has_brand_match)
            total_score = self.assign_score(overwrite=overwrite, score=product_code_score,
                                            total_score=total_score)
            # Rule 3 : calculate attribute score when total_score < threshold
            if total_score < self.confidence_threshold:
                attrs_score, overwrite = self.get_attrs_match_score(each_offer, total_score, has_brand_match)
                total_score = self.assign_score(overwrite=overwrite, score=attrs_score,
                                                total_score=total_score)
            # Rule 4 : calculate brand score when total_score < threshold
            if total_score < self.confidence_threshold:
                brand_score, overwrite = self.get_brand_match_score(each_offer, total_score, has_brand_match)
                total_score = self.assign_score(overwrite=overwrite, score=brand_score,
                                                total_score=total_score)
            # Rule 5 : re-score manual matched offers
            if total_score == 2.0:
                new_total_score, overwrite = self.rescore_confidence_score(each_offer, total_score, has_brand_match)
                if overwrite:
                    total_score = self.assign_score(overwrite=overwrite, score=new_total_score,
                                                    total_score=total_score)

            # total_score = text_score + product_score + attrs_score + brand_score

            each_offer = self.support.score_classification(total_score, each_offer)
            each_offer.ops_score = total_score
            each_offer.text_score = text_score
            each_offer.product_code_score = product_code_score
            each_offer.attrs_score = attrs_score
            each_offer.brand_score = brand_score

            if each_offer.source == "gs" or each_offer.source == "gp":
                if total_score > self.gs_threshold:
                    offer_processed.append(each_offer)
            elif not self.apply_threshold:
                offer_processed.append(each_offer)
            else:
                if total_score > self.min_lb_threshold:
                    offer_processed.append(each_offer)
                    message.append(dict(score=total_score, name=name, title=input_title,
                                        hits_confidence=each_offer.ops_score,
                                        source=each_offer.source,
                                        id=each_offer.id, product_id=each_offer.product_id, store=each_offer.store_name,
                                        price=each_offer.price))

        logger.info(dict(correlation_id=SConfig.correlation_id,
                         source='calculate_confidence_helper', result=message))
        return offer_processed

    def calculate_confidence_v2(self, offer_attrs: Dict, offers: List[Offer]) -> List[Offer]:
        """
                Action : Method to calcuate confidence score for each offers using input offer_attrs
                Conditions :
                1.Looping through all the offers
                2.Calculate title match score against input offer
                3.Calculate product code match score (gtin,asin,upc,isbn,ean) score against input offer
                4.Calculate attrs score against input when score < threshold
                5.Calculate brand match score against input when score < threshold
        """
        offer_processed = []
        # ToDo: refactor this to send offer_attrs directly to the method instead of using the object itself
        self.offer_attrs = offer_attrs
        input_title = self.support.clean_text(self.offer_attrs.get("title"))
        brand = self.support.clean_text(str(self.offer_attrs.get("brand") or ''))
        input_title = f"{brand} {input_title}" if brand not in input_title else input_title
        message = []
        for each_offer in offers:
            text_score = 0.0
            attrs_score = 0.0
            product_code_score = 0.0
            brand_score = 0.0
            image_score = 0.0
            total_score = 0.0
            has_brand_match = False

            name = self.support.clean_text(each_offer.title)
            has_brand_match = self.__is_brand_match(each_offer)

            # Rule 1 : calculate text score
            text_score = self.support.get_cosine(input_title, name)
            total_score = text_score

            # Rule 2 : calculate product code score(gtin,mpn,upc,isbn,ean,gpid,product_id)
            product_code_score, overwrite = self.get_product_code_match_score(each_offer, total_score, has_brand_match)
            total_score = self.assign_score(overwrite=overwrite, score=product_code_score,
                                            total_score=total_score)
            each_offer.product_code_score = product_code_score



            # Rule 3: Image score rules
            image_score, overwrite = self.get_image_match_score(each_offer, total_score)
            total_score = self.assign_score(overwrite=overwrite, score=image_score,
                                            total_score=total_score)

            # Rule 4 : calculate attribute score when total_score < threshold
            if product_code_score < 1.5 or product_code_score == 2.0:
                attrs_score, overwrite = self.get_attrs_match_score(each_offer, total_score, has_brand_match)
                total_score = self.assign_score(overwrite=overwrite, score=attrs_score,
                                                total_score=total_score)

            # Rule 5 : calculate brand score when total_score < threshold
            if total_score < self.confidence_threshold:
                brand_score, overwrite = self.get_brand_match_score(each_offer, total_score, has_brand_match)
                total_score = self.assign_score(overwrite=overwrite, score=brand_score,
                                                total_score=total_score)

            # Rule 6 : re-score manual matched offers
            if product_code_score == 2.0:
                new_total_score, overwrite = self.rescore_confidence_score(each_offer, total_score, has_brand_match)
                if overwrite:
                    total_score = self.assign_score(overwrite=overwrite, score=new_total_score,
                                                    total_score=total_score)
            # Rule7 : Exclude Market List
            if total_score > self.confidence_threshold:
                new_total_score, overwrite = self.market_place_rules(each_offer, total_score)
                total_score = self.assign_score(overwrite=overwrite, score=new_total_score,
                                                total_score=total_score)

            # total_score = text_score + product_score + attrs_score + brand_score

            each_offer = self.support.score_classification(total_score, each_offer)
            each_offer.ops_score = total_score
            each_offer.text_score = text_score
            each_offer.product_code_score = product_code_score
            each_offer.attrs_score = attrs_score
            each_offer.brand_score = brand_score
            each_offer.image_score = image_score

            if each_offer.source == "gs" or each_offer.source == "gp":
                if total_score > self.gs_threshold:
                    offer_processed.append(each_offer)
            elif not self.apply_threshold:
                offer_processed.append(each_offer)
            else:
                if total_score > self.min_lb_threshold:
                    offer_processed.append(each_offer)
                    message.append(dict(score=total_score, name=name, title=input_title,
                                        hits_confidence=each_offer.ops_score,
                                        source=each_offer.source,
                                        id=each_offer.id, product_id=each_offer.product_id, store=each_offer.store_name,
                                        price=each_offer.price))

        logger.info(dict(correlation_id=SConfig.correlation_id,
                         source='calculate_confidence_helper', result=message))

        return offer_processed

    # ToDo: Document this method
    def assign_score(self, overwrite: bool, score: float, total_score: float) -> float:
        """
                Action : Assign and return total_score with given criteria
                Conditions :
                when overwrite = True then overwrite given score as total_score
                when overwrite = False then add the score to total_score
        """
        if overwrite:
            total_score = score
        else:
            total_score += score
        return total_score

    def market_place_rules(self, offer: Offer, total_score: float) -> Tuple[float, bool]:
        """
        Action : overwriting the scores
        Conditions   : multiple rules based on retailer
        """
        score = 0.0
        overwrite = False
        # Rescore the same stores in top match
        if offer.store_name and offer.store_name not in self.top_match_stores:
            self.top_match_stores.append(offer.store_name)
        elif offer.store_name and offer.store_name in self.top_match_stores:
            score = 0.89
            overwrite = True
        return score, overwrite


    def get_brand_match_score(self, offer: Offer, total_score: float, has_brand_match: bool) -> Tuple[float, bool]:
        """
        Action : Boost the score by 0.05
        Conditions   : brand matched and brand not in title
        """
        score = 0.0
        overwrite = False
        title = (offer.title or "").lower()
        if has_brand_match and offer.brand not in title:
            score = score + 0.05
        return score, overwrite

    def get_image_match_score(self, offer: Offer, total_score: float) -> Tuple[float, bool]:
        image_score = 0.0
        overwrite = False
        if self.offer_attrs.get("department_name").lower() == "fashion":
            if not offer.image_score:
                # BE-632 negatively boost text match offers if no associated image set
                if offer.product_code_score < 1.5:
                    image_score = self.support.get_boosting_factor(0.7) * total_score
            else:
                if offer.is_only_img_match or offer.product_code_score < 1.5:
                    image_score = self.support.get_boosting_factor(offer.image_score) * total_score

        elif self.offer_attrs.get("department_name").lower() == "health & beauty":
            if offer.product_code_score < 1.5 and offer.image_score:
                image_score = self.support.health_beauty_boosting_factor(offer.image_score)
                if image_score >= 0.95:
                    overwrite = True
                else:
                    image_score = image_score * total_score

        return image_score, overwrite

    def __is_brand_match(self, offer: Offer):
        has_matched = \
            (self.offer_attrs.get("brand_name") and self.offer_attrs.get("brand_name") == offer.brand_name) \
            or (self.offer_attrs.get("brand") and self.offer_attrs.get("brand") == offer.brand)
        return has_matched

    def rescore_confidence_score(self, offer: Offer, total_score: float, has_brand_match: bool) -> Tuple[float, bool]:
        unmatch_count = 0
        score = total_score
        overwrite = False
        if not has_brand_match:
            unmatch_count += 1
        if self.offer_attrs.get("mpn") and offer.mpn and not self.offer_attrs.get("mpn") == offer.mpn:
            unmatch_count += 1

        # ToDo: add comment on what is this function and statements in code logic trying to achieve
        for each_attr_key, each_attr_value in self.offer_attrs.get("neg_attrs").items():
            offer_attr = None
            if offer.neg_attrs.get(each_attr_key):
                offer_attr = (offer.neg_attrs.get(each_attr_key).get("value") or "").lower()

            if offer_attr and each_attr_value.get("value") and \
                    not each_attr_value.get("value").lower() == offer_attr:
                unmatch_count += 1

        if unmatch_count >= 2:
            score = 0.91
            overwrite = True
        return score, overwrite

    def get_product_code_match_score(self, offer: Offer, total_score: float, has_brand_match: bool) -> Tuple[
        float, bool]:
        """
        Action : Boost the score based on different product code match
        Conditions :
        If Department = Department & GTIN = GTIN ; Set confidence to 1.88
        else If Brand = Brand & MPN = MPN; Set confidence to 1.87
        else If Department = Department & UPC = UPC ; Set confidence to 1.85
        else If Department = Department & ISBN = ISBN ; Set confidence to 1.82
        else If Department = Department & EAN = EAN ; Set confidence to 1.79
        else If GPID= GPID ; Set confidence to 1.5
        else if Legacy Product ID = Legacy Product Id; Set confidence to 2.00

        If ASIN = ASIN; Positive Boost Conf score by 15%
        """
        input_department = self.offer_attrs.get("department_name")
        brand = self.offer_attrs.get("brand")
        brand_name = self.offer_attrs.get("brand_name")
        overwrite = False
        input_attrs = self.offer_attrs.get("attrs")
        offer_attrs_transform = offer.attrs

        score = 0.0

        if input_department and input_department == offer.department_name:
            if self.offer_attrs.get("gtin") and (
                    self.offer_attrs.get("gtin") == offer.gtin or offer.gtin in self.offer_attrs.get("product_codes")):
                score = 1.88
                overwrite = True
            elif self.offer_attrs.get("upc") and (
                    self.offer_attrs.get("upc") == offer.upc or offer.upc in self.offer_attrs.get("product_codes")):
                score = 1.85
                overwrite = True
            elif self.offer_attrs.get("isbn") and (
                    self.offer_attrs.get("isbn") == offer.isbn or offer.isbn in self.offer_attrs.get("product_codes")):
                score = 1.82
                overwrite = True
            elif self.offer_attrs.get("ean") and (
                    self.offer_attrs.get("ean") == offer.ean or offer.ean in self.offer_attrs.get("product_codes")):
                score = 1.79
                overwrite = True
        if not overwrite and has_brand_match:
            if self.offer_attrs.get("mpn") and self.offer_attrs.get("mpn") == offer.mpn:
                score = 1.87
                overwrite = True

            if input_attrs.get("size") and input_attrs.get("size") == offer_attrs_transform.get("size") \
                    and input_attrs.get("colour") and input_attrs.get("colour") == offer_attrs_transform.get("colour"):
                if self.offer_attrs.get("mpn") and self.offer_attrs.get("mpn") == offer_attrs_transform.get(
                        "model_name"):
                    score = 1.87
                    overwrite = True
                if input_attrs.get("model_name") and input_attrs.get("model_name") == offer.mpn:
                    score = 1.87
                    overwrite = True

        if not overwrite and self.offer_attrs.get("gpid") and self.offer_attrs.get("gpid") == offer.gpid:
            score = 1.5
            overwrite = True

        if not overwrite and self.offer_attrs.get("product_id") and str(self.offer_attrs.get("product_id")) == str(
                offer.product_id or ""):
            score = 2.0
            overwrite = True

        if score > 0.0 and overwrite:
            return score, overwrite

        # ToDo: Revisit these rules later, appending to scores for now if product id match
        # if self.offer_attrs.get("product_id") and str(self.offer_attrs.get("product_id")) == str(
        #         offer.product_id or ""):
        #     score = score + (total_score * 0.3)
        #     total_score = total_score + score
        #     overwrite = False
        # if self.offer_attrs.get("asin") and self.offer_attrs.get("asin") == offer.asin:
        #     score = score + (total_score * 0.15)
        #     overwrite = False

        if self.offer_attrs.get("asin") and self.offer_attrs.get("asin") == offer.asin:
            score = score + (score * 0.15)
            overwrite = False

        return score, overwrite

    def get_product_taxonomy_match_score(self, offer: Offer) -> float:
        """
                Action : returns taxonomy match score with given criteria
                Conditions :
                When department matched then 1
                When category  matched then 2
                When sub_category  matched then 3
        """
        score = 0.0
        input_department = self.offer_attrs.get("department_name", "").lower()
        input_category = self.offer_attrs.get("category_name", "").lower()
        input_subcategory = self.offer_attrs.get("subcategory_name", "").lower()

        if input_department and offer.department_name and input_department == offer.department_name.lower():
            score += 1.0
        if input_category and offer.category_name and input_category == offer.category_name.lower():
            score += 2.0
        if input_subcategory and offer.subcategory_name and input_subcategory == offer.subcategory_name.lower():
            score += 3.0
        return score

    def get_attrs_match_score(self, offer: Offer, total_score: float, has_brand_match: bool) -> Tuple[float, bool]:
        """
                       Action : returns attrs match score
                       Conditions :
                       1.When Fashion and taxonomy_score >= 1 (atleast dept should match)
                            1.a. positive boost - when brand and colour matches boost 25% of given score
                            1.b. negative boost - when colour does not matches set the score as 0.89
                            1.c attrs_score  = (positive boost- negative boost)
                       2.When Other department and taxonomy_score >= 6 (subcat should match)
                            2.a. positive boost - when brand and model_name matches boost 40% of given score
                            2.b. negative boost - when colour,condition,capacity,size if anyone does not matches and not null negative boost 35% of given score
                            2.c. negative boost - when colour,condition,capacity,size if multiple does not matches set the score as 0.89
                            2.d attrs_score  = (positive boost- negative boost)
                       3.Else
                           attrs_score= 0

        """
        score = 0.0
        matched_count = 0
        unmatch_count = 0
        overwrite = False
        gender_match = True
        if len(self.offer_attrs.get("pos_attrs")) + len(self.offer_attrs.get("neg_attrs")) == 0:
            return score, overwrite

        taxonomy_score = self.get_product_taxonomy_match_score(offer)
        model_name_match = False
        if taxonomy_score == 6.0 or (self.offer_attrs.get("department_name").lower() == "fashion" \
                                     and taxonomy_score >= 1.0):
            # positive attrs boosting
            for each_attr_key, each_attr_value in self.offer_attrs.get("pos_attrs").items():
                offer_attr = None
                if total_score > self.confidence_threshold:
                    break
                if offer.pos_attrs.get(each_attr_key):
                    offer_attr = (offer.pos_attrs.get(each_attr_key).get("value") or "").lower()

                if each_attr_value.get("value") and offer_attr and \
                        each_attr_value.get("value").lower() == offer_attr:
                    if each_attr_key == "model_name":
                        model_name_match = True
                    else:
                        matched_count += 1
            if model_name_match and matched_count > 0:
                score = score + (total_score * 0.40)
                total_score = total_score + score

            # negative attrs boosting
            if not has_brand_match:
                unmatch_count += 1
            if self.offer_attrs.get("mpn") and offer.mpn and not self.offer_attrs.get("mpn") == offer.mpn:
                unmatch_count += 1

            for each_attr_key, each_attr_value in self.offer_attrs.get("neg_attrs").items():
                offer_attr = None
                if offer.neg_attrs.get(each_attr_key):
                    offer_attr = (offer.neg_attrs.get(each_attr_key).get("value") or "").lower()
                if each_attr_value.get("value") and offer_attr and \
                        not each_attr_value.get("value").lower() == offer_attr:
                    if each_attr_key == "condition":
                        if total_score > 0.79:
                            score = 0.79
                            overwrite = True
                        else:
                            score = 0.0
                        return score,overwrite
                    elif each_attr_key == "gender" \
                            and self.offer_attrs.get("department_name").lower() == "fashion":
                        gender_match = False
                    else:
                        unmatch_count += 1
            if unmatch_count > 1 and total_score > 0.89:
                score = 0.89
                overwrite = True
            elif not  gender_match:
                score = score - (total_score * 0.50)
                total_score = total_score + score
            elif unmatch_count > 1:
                score = 0.0
            elif unmatch_count == 1:
                score = score - (total_score * 0.35)
                total_score = total_score + score

        elif taxonomy_score >= 1.0 and self.offer_attrs.get("department_name").lower() == "health & beauty":
            for each_attr_key, each_attr_value in self.offer_attrs.get("neg_attrs").items():
                offer_attr = None
                if offer.neg_attrs.get(each_attr_key):
                    offer_attr = (offer.neg_attrs.get(each_attr_key).get("value") or "").lower()
                if each_attr_value.get("value") and offer_attr and \
                        not each_attr_value.get("value").lower() == offer_attr:
                    if each_attr_key == "size":
                        score = score - (total_score * 0.20)
                        total_score = total_score + score
                    if each_attr_key == "colour":
                        score = score - (total_score * 0.30)
                        total_score = total_score + score
            if self.offer_attrs.get("mpn") and offer.mpn and not self.offer_attrs.get("mpn") == offer.mpn:
                score = score - (total_score * 0.40)
                total_score = total_score + score
            if not has_brand_match:
                score = score - (total_score * 0.84)
                total_score = total_score + score
        return score, overwrite
