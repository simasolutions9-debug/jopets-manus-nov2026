from dataclasses import dataclass
from decimal import Decimal
from django.utils import timezone
from .models import PriceRule
@dataclass(frozen=True)
class PublishedPrice:
    country:str; category:str; currency:str; amount:Decimal; ppp_factor:Decimal; version:int; detection_method:str
def published_price(country,category,detection_method):
    rule=PriceRule.objects.filter(country=country.upper(),category=category,published=True,valid_from__lte=timezone.now()).order_by("-version").first()
    if not rule: return None
    return PublishedPrice(rule.country,rule.category,rule.currency,(rule.base_price*rule.ppp_factor).quantize(Decimal("0.01")),rule.ppp_factor,rule.version,detection_method)
