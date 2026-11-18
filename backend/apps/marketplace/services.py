from decimal import Decimal, ROUND_DOWN


def points_for_order(total, currency, status):
    amount = Decimal(str(total))
    if str(currency).upper() != "USD" or str(status).lower() not in {"paid", "captured", "succeeded"} or amount <= 0:
        return 0
    return int(amount.quantize(Decimal("1"), rounding=ROUND_DOWN))


def discount_from_points(points):
    points = int(points)
    if points < 0:
        raise ValueError("Los puntos no pueden ser negativos")
    return (Decimal(points) / Decimal("100")).quantize(Decimal("0.01"))


def validate_referral(inviter_id, invitee_id, code, already_used):
    if not code or not str(code).strip():
        raise ValueError("Código de referido obligatorio")
    if str(inviter_id) == str(invitee_id):
        raise ValueError("No se permite autoreferido")
    if already_used:
        raise ValueError("El referido ya fue utilizado")
    return Decimal("0.00")
