from django.db import models
from django.db.models import Q


HOUSE_TYPE = (
    ('c', 'Condo'),
    ('h', 'HDB'),
)


class Transaction(models.Model):

    CONDO = 'c'
    HDB = 'b'

    type = models.CharField(max_length=1, choices=HOUSE_TYPE, default='h')
    name = models.CharField(max_length=200, null=True, blank=True)
    room_count = models.IntegerField(null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    month = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    area_sqm_min = models.FloatField(null=True, blank=True)
    area_sqm_max = models.FloatField(null=True, blank=True)
    monthly_rent = models.FloatField(null=True, blank=True)
    area_sqft_min = models.FloatField(null=True, blank=True)
    area_sqft_max = models.FloatField(null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __unicode__(self):
        return ", ".join((self.type, str(self.address), str(self.year), str(self.month)))

    def print_transaction(self):
        print "name: {0}; room_count: {1}; year: {2}; month: {3}; address: {4}; postal_code: {5}; " \
              "area_sqm_min: {6}; area_sqm_max: {7}; monthly_rent: {8}; type: {9}".format(
                self.name,
                self.room_count,
                self.year,
                self.month,
                self.address,
                self.postal_code,
                self.area_sqm_min,
                self.area_sqm_max,
                self.monthly_rent,
                self.type
        )


    @staticmethod
    def get_transactions(transactions=None, type=None, postal_code=None, name=None, address=None, room_count=None):
        """
        Get transactions satisfied some specified features
        Consider only transactions in original transaction list
        :param transactions: original transaction list
        :param type:
        :param postal_code:
        :param name:
        :param address:
        :param room_count:
        :return:
        """
        query = Q(id__gt=0)
        if type:
            query = query & Q(type=type)
        if name:
            query = query & Q(name=name)
        if address:
            query = query & Q(address=address)
        if room_count:
            if room_count == 'u':
                query = query & Q(room_count=None)
            elif room_count != "":
                query = query & Q(room_count=room_count)
        if postal_code:
            query = query & Q(postal_code=postal_code)
        transactions = Transaction.objects.filter(query)
        return transactions



