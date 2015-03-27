import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "spms_site.settings")

import django
django.setup()


from transactions.models import Transaction


def convert_from_sqm_to_sqft(sqm):
    return sqm * 10.7639


def convert_from_sqft_to_sqm(sqft):
    return sqft * 0.092903


def init_hdb_areasqft():
    transactions = Transaction.objects.filter(type="h")

    for transaction in transactions:
        if transaction.area_sqm_min:
            transaction.area_sqft_min = convert_from_sqm_to_sqft(transaction.area_sqm_min)
        if transaction.area_sqm_max:
            transaction.area_sqft_max = convert_from_sqm_to_sqft(transaction.area_sqm_max)
        transaction.save()
    print "done1"


def init_condo_area_sqm():
    transactions = Transaction.objects.filter(type="c")

    for transaction in transactions:
        if transaction.area_sqm_min:
            transaction.area_sqft_min = convert_from_sqft_to_sqm(transaction.area_sqm_min)
        if transaction.area_sqm_max:
            transaction.area_sqft_max = convert_from_sqft_to_sqm(transaction.area_sqm_max)
        transaction.area_sqft_min, transaction.area_sqm_min = transaction.area_sqm_min, transaction.area_sqft_min
        transaction.area_sqft_max, transaction.area_sqm_max = transaction.area_sqm_max, transaction.area_sqft_max
        transaction.save()
    print "done2"


if __name__ == '__main__':
    init_hdb_areasqft()
    # init_condo_area_sqm()