from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Protocol

@dataclass(frozen=True)
class PaymentRoute:
    provider_country: str
    customer_country: str
    gateway: str
    currency: str
    mode: str = "sandbox"

@dataclass(frozen=True)
class PaymentResult:
    operation_id: str
    status: str
    amount: Decimal
    currency: str
    simulated: bool

class PaymentAdapter(Protocol):
    name: str
    def authorize(self, amount: Decimal, currency: str, idempotency_key: str) -> PaymentResult: ...
    def capture(self, operation_id: str, idempotency_key: str) -> PaymentResult: ...
    def refund(self, operation_id: str, amount: Decimal, idempotency_key: str) -> PaymentResult: ...

class SandboxAdapter:
    def __init__(self, name): self.name=name; self._operations={}
    def _result(self, key, status, amount=Decimal("0"), currency="USD"):
        if key in self._operations: return self._operations[key]
        result=PaymentResult(f"sandbox_{self.name}_{key}",status,amount,currency,True); self._operations[key]=result; return result
    def authorize(self, amount, currency, idempotency_key): return self._result(idempotency_key,"authorized",Decimal(amount),currency)
    def capture(self, operation_id, idempotency_key): return self._result(idempotency_key,"captured")
    def refund(self, operation_id, amount, idempotency_key): return self._result(idempotency_key,"refunded",Decimal(amount))

class PaymentGatewayFactory:
    def __init__(self, routes): self.routes=routes
    def select(self, provider_country, customer_country):
        matches=[r for r in self.routes if r.provider_country==provider_country and r.customer_country==customer_country and r.mode=="sandbox"]
        gateways={r.gateway for r in matches}
        if len(matches)!=1 or len(gateways)!=1: raise LookupError("Ruta de pago ausente o ambigua")
        return matches[0]
    def adapter(self, route):
        if route.gateway not in {"payphone","kushki","stripe","dlocal"}: raise LookupError("Pasarela no soportada")
        return SandboxAdapter(route.gateway)

def split_net(amount, processor_fixed, processor_rate, provider_pct, subowner_pct):
    amount=Decimal(str(amount)); fixed=Decimal(str(processor_fixed)); rate=Decimal(str(processor_rate))
    net=(amount-fixed-(amount*rate)).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)
    provider=Decimal(str(provider_pct)); subowner=Decimal(str(subowner_pct)); sima=Decimal("100")-provider-subowner
    if min(provider,subowner,sima)<0 or provider+subowner+sima!=Decimal("100"): raise ValueError("El reparto debe sumar 100%")
    return {"gross":amount,"processor_cost":(amount-net),"net":net,"provider":(net*provider/100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP),"subowner":(net*subowner/100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP),"sima":(net*sima/100).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP)}
