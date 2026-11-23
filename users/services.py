import stripe

from config.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY


def create_stripe_price(amount, course_name):
    """Создает цену в Stripe."""

    price = stripe.Price.create(
        currency="usd",
        unit_amount=int(amount * 100),
        product_data={"name": course_name},
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


def get_payment_status(session_id):
    """Проверяет статус оплаты по id сессии"""

    session = stripe.checkout.Session.retrieve(session_id)

    return session.payment_status
