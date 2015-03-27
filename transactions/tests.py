from django.test import TestCase

# Create your tests here.
from transactions.charts import Chart
from transactions.models import Transaction
from transactions.transaction_util import is_coordinate_neighbor, get_transactions_by_neighbor_postal_code, \
    is_same_property, weighted_avg_price, get_transactions_by_property, get_transactions_by_neighbor_coordinate_property


class UtilTest(TestCase):

    def test_is_same_property(self):
        trans1 = Transaction(id=1, address="1", postal_code="1")
        trans2 = Transaction(id=2, address="2", postal_code="1")
        trans3 = Transaction(id=3, address="2", postal_code="3")
        trans4 = Transaction(id=4, address="2", postal_code="1")
        self.assertEquals(is_same_property(trans1, trans2), False)
        self.assertEquals(is_same_property(trans2, trans3), False)
        self.assertEquals(is_same_property(trans2, trans4), True)

    def test_is_coordinate_neighbor(self):
        trans1 = Transaction(latitude=0.005, longitude=0.000, address="1")
        trans2 = Transaction(latitude=0.000, longitude=-0.005, address="2")
        trans3 = Transaction(latitude=-0.005, longitude=-0.001, address="3")
        self.assertEquals(is_coordinate_neighbor(trans1, trans2), True)
        self.assertEquals(is_coordinate_neighbor(trans1, trans3), False)
        self.assertEquals(is_coordinate_neighbor(trans2, trans3), True)
        self.assertEquals(is_coordinate_neighbor(trans1, trans1), True)


class ChartAndUtilTest(TestCase):

    def setUp(self):
        transaction_list = [
            # postalcode, address, long, lat, price
            ["123456", "Address 1", "1.3", "103.9", 1000],
            ["123456", "Address 1", "1.3", "103.9", 2000],
            ["123455", "Address 2", "1.305", "103.905", 500],
            ["123452", "Address 3", "1.302", "103.901", 100],
            ["123451", "Address 4", "1.35", "103.95", 10],  # neighbor postal_code but not neighbor address
            ["123401", "Address 5", "1.301", "103.901", 2000],  # not neighbor postal_code but neighbor address
            ["123400", "Address 6", "1.29", "104", 3000],
            ["123400", "Address 6", "1.29", "104", 4000],

        ]
        for transaction in transaction_list:
            trans = Transaction(postal_code=transaction[0],
                                address=transaction[1],
                                longitude=transaction[2],
                                latitude=transaction[3],
                                monthly_rent=transaction[4],
                                month=1, year=2012)
            trans.save()

    def test_get_transactions_by_neighbor_postal_code(self):
        transactions = get_transactions_by_neighbor_postal_code(postal_code="123456")
        self.assertEquals(len(transactions), 5)
        for trans in transactions:
            self.assertEquals(trans.postal_code[:len(trans.postal_code)-1], "12345")

    def test_get_transactions_by_neighbor_address(self):

        property = Transaction.get_transactions(postal_code="123456")[0]

        # Test include=True
        transactions = get_transactions_by_neighbor_coordinate_property(property=property, include=True)
        self.assertEquals(len(transactions), 5)

        # Test include=False
        transactions = get_transactions_by_neighbor_coordinate_property(property=property, include=False)
        self.assertEquals(len(transactions), 3)
        for trans in transactions:
            self.assertEquals(is_same_property(trans, property), False)

    def test_get_transactions_by_property(self):
        property = Transaction.objects.filter(postal_code="123400")[0]

        self.assertEquals(get_transactions_by_property(transactions=[], property=property), [])
        self.assertEquals(len(get_transactions_by_property(property=property)), 2)
        self.assertEquals(len(get_transactions_by_property(Transaction.objects.all()[:7], property=property)), 1)

    def test_weighted_avg_price(self):
        self.assertEquals(weighted_avg_price(price_by_addr=None, price_by_neighbor_addr=3.4), 3.4)
        self.assertEquals(weighted_avg_price(price_by_addr=2, price_by_neighbor_addr=3), 2.2)

    def test_chart_retrieve(self):
        chart = Chart.chart_retrieve(Transaction.objects.all())
        self.assertEquals(len(chart['count']), 37)
        self.assertEquals(chart['count'][0], 8)
        self.assertEquals(chart['price'][0], 12610/8)




