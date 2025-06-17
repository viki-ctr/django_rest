import stripe
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY


def create_stripe_product(name, description):
    return stripe.Product.create(
        name=name,
        description=description
    )


def create_stripe_price(product_id, amount, currency='rub'):
    return stripe.Price.create(
        product=product_id,
        unit_amount=int(amount * 100),
        currency=currency
    )


def create_stripe_checkout_session(price_id, success_url, cancel_url):
    return stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )


def get_stripe_session_status(session_id):
    session = stripe.checkout.Session.retrieve(session_id)
    return session.payment_status
