from transactions.transaction_util import get_transactions_by_neighbor_postal_code, \
    weighted_avg_price, get_transactions_by_neighbor_coordinate_property, get_transactions_by_property


class Chart(object):
    ITSELF = 'i'
    NEIGHBOR_POSTALCODE = 'p'
    NEIGHBOR_COORDINATE = 'c'

    CHART_SERIES_CHOICES = (
        (ITSELF, 'Itself'),
        (NEIGHBOR_POSTALCODE, 'Neighbor Postal Code'),
        (NEIGHBOR_COORDINATE, 'Neighbor Coordinate'),
    )

    LIST_CHOICES = (
        (ITSELF, 'Itself'),
        (NEIGHBOR_POSTALCODE, 'Neighbor Postal Code'),
        (NEIGHBOR_COORDINATE, 'Neighbor Coordinate'),
    )

    @staticmethod
    def chart_retrieve(transactions):
        """
        Return a dictionary from transactions
        chart {
            'count': int[]
            'price': int[]
        }
        count[i]: Number of transactions in period i
        price[i]: Average price of transactions in period i

        For now, periods from 01/2012 --> 01/2015
        """
        cnt = [[0 for month in range(0, 13)] for year in range(0, 2016)]
        amt = [[0 for month in range(0, 13)] for year in range(0, 2016)]
        for transaction in transactions:
            if transaction.year and transaction.month and transaction.monthly_rent:
                year, month = transaction.year, transaction.month
                cnt[year][month] += 1
                amt[year][month] += transaction.monthly_rent

        chart = {'count': [], 'price': []}
        for year in range(2012, 2016):
            for month in range(1, 13):
                if year < 2015 or month == 1:
                    if cnt[year][month] > 0:
                        chart['price'].append(round(amt[year][month] / cnt[year][month]))
                    else:
                        chart['price'].append(None)
                    chart['count'].append(cnt[year][month])
        return chart

    @staticmethod
    def chart_avg_by_property(transactions, property):
        """
        Return dictionary (chart dict) from transactions whose property=specified property
        Consider only transactions from original transaction list
        :param transactions: original transaction list
        :param property: specified property
        :return:
        """
        transactions = get_transactions_by_property(transactions=transactions, property=property)
        return Chart.chart_retrieve(transactions)

    @staticmethod
    def chart_avg_by_neighbor_coordinate_property(transactions, property):
        """
        Return dictionary (chart dict) from transactions which is a coordinate-neighbor of specified property
        Consider only transactions from original transaction list
        :param transactions: original transaction list
        :param property: specified property. A property is represented by a transaction
        :return:
        """
        transactions = get_transactions_by_neighbor_coordinate_property(transactions, property, include=False)
        return Chart.chart_retrieve(transactions)

    @staticmethod
    def chart_by_neighbor_coordinate_property(transactions, property):
        """
        Return dictionary (chart dict) from transactions which is a address-neighbor of specified property
        Consider only transactions from original transaction list

        :param transactions: original transaction list
        :param property: specified property. A property is a transaction
        :return:

        The weighted average price is calculated as below:
            For each property A = (x1,y1), where x and y are coordinates of A, to compute the average price of A for each month and corresponding search query,
            first compute a set of properties, denoted by S, where B = (x2,y2) is in S if
            -- (i) B is not equal to A, and,
            -- (ii) |x1 - x2| <= 0.005 and |y1 - y2| <= 0.005.
            That is S includes those places close to A except A itself.

            Then the average price for each month of A is computed as follows:
            1. If price in A is not empty, then average price = 0.8 * A + 0.2 * average prices of those in S.
            2. If price in A is empty, then average price = average prices of those in S.
        """
        avg_by_property = Chart.chart_avg_by_property(transactions, property)
        avg_by_neighbor_coordinate_property = Chart.chart_avg_by_neighbor_coordinate_property(transactions, property)

        chart = {'price': [], 'count': []}
        for i in range(len(avg_by_property['price'])):
            chart['price'].append(weighted_avg_price(avg_by_property['price'][i], avg_by_neighbor_coordinate_property['price'][i]))
            chart['count'].append(avg_by_property['count'][i] + avg_by_neighbor_coordinate_property['count'][i])
        return chart

    @staticmethod
    def chart_by_neighbor_postal_code(transactions=None, postal_code=None):
        """
        Return a dictionary (chart dict) from postal_code-neighbor transactions
        Consider transactions in the original transactions list
        :param transactions: original transaction list
        :param postal_code: specified postal_code
        :return:
        """
        transactions = get_transactions_by_neighbor_postal_code(transactions, postal_code)
        return Chart.chart_retrieve(transactions)
