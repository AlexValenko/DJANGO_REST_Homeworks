import stripe
from config.settings import STRIPE_API_KEY

stripe.api_key =STRIPE_API_KEY


def create_stripe_price(amount):
    """Создает цену в Stripe."""

    price = stripe.Price.create(
        currency="usd",
        unit_amount=int(amount * 100),
        product_data={"name": "Course"},
    )
    return price

def create_stripe_sessions(price):
    """Создание сессии в Srtipe"""

    session = stripe.checkout.Session.create(
        success_url="http://127.0.0.1:8000/",
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
    )
    return session.id, session.url