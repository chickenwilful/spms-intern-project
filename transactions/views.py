from django.http import HttpResponse
from django.shortcuts import render

import logging
logger = logging.getLogger(__name__)

from transactions.charts import Chart
from transactions.forms import FilterForm, ChartFilterForm
from transactions.models import Transaction
from transactions.transaction_util import get_transactions_by_neighbor_postal_code, \
    get_transactions_by_neighbor_coordinate_property


def get_google_map_coordinates(request, template='map.html'):
    """
    A view to get gg map co-ordinate of all transactions whose latitude is None
    """
    transactions = Transaction.objects.filter(latitude__isnull=True)
    postalcodes = set([trans.postal_code for trans in transactions])
    return render(request, template, {
        'count': len(postalcodes),
        'postal_codes': postalcodes}
    )


def update_coordinate(request):
    """
    View to update gg map co-ordinate of a particular transactions by request.GET
    An example request: /coordinate?postalcode=123456&lat=103.1&lng=102.2
    """
    if request.GET:
        postal_code, lat, lng = request.GET['postalcode'], request.GET['lat'], request.GET['lng']
        transactions = Transaction.objects.filter(postal_code=postal_code)
        for trans in transactions:
            trans.latitude, trans.longitude = lat, lng
            trans.save()
        logger.debug("%d transactions updated!" % len(transactions))
        return HttpResponse("Transactions updated!")
    else:
        return HttpResponse("Not GET request")


def transaction_list(request, template="transaction_list.html"):
    """
    View to display transactions list and related charts.
    """
    MAX_LENGTH = 50  # Maximum number of transactions to be displayed

    if not (request.POST or request.GET):
        # get all transactions
        transactions = Transaction.objects.all()

        # chart contains only average price of all transactions
        charts = {
            'by_itself': Chart.chart_retrieve(transactions)
        }

        result_count = len(transactions)
        if len(transactions) > MAX_LENGTH:
            transactions = transactions[:MAX_LENGTH]

        return render(request, template, {'transactions': transactions,
                                          'result_count': result_count,
                                          'chart': charts,
                                          'filter_form': FilterForm(),
                                          'chart_form': ChartFilterForm()})
    else:  # if request.POST or request.GET
        # Handle the POST request
        chart_filter_form = ChartFilterForm(request.POST)
        filter_form = FilterForm(request.POST, one_property=chart_filter_form.get_one_property())

        if filter_form.is_valid():

            type = filter_form.cleaned_data['type']
            room_count = filter_form.cleaned_data['room_count']

            transactions = Transaction.get_transactions(type=type, room_count=room_count)
            property = filter_form.get_property()
            filtered_transactions = filter_form.get_transactions()

            charts = {}
            # Handle chart series
            chart_series = request.POST.getlist('series')
            if Chart.ITSELF in chart_series:
                charts['by_itself'] = Chart.chart_retrieve(filtered_transactions)
            if Chart.NEIGHBOR_POSTALCODE in chart_series:
                charts['by_postalcode'] = Chart.chart_by_neighbor_postal_code(transactions, property.postal_code)
            if Chart.NEIGHBOR_COORDINATE in chart_series:
                charts['by_coordinate'] = Chart.chart_by_neighbor_coordinate_property(transactions, property)

            # Handle displayed list
            display_list = request.POST['list']
            if display_list == Chart.ITSELF:
                transactions = filtered_transactions
            elif display_list == Chart.NEIGHBOR_POSTALCODE:
                transactions = get_transactions_by_neighbor_postal_code(transactions, property.postal_code)
            else:  # display_list == Chart.NEIGHBOR_COORDINATE
                transactions = get_transactions_by_neighbor_coordinate_property(transactions, property, include=True)

            result_count = len(transactions)
            if len(transactions) > MAX_LENGTH:
                transactions = transactions[:MAX_LENGTH]
            return render(request, template, {'transactions': transactions,
                                              'result_count': result_count,
                                              'filter_form': FilterForm(request.POST),
                                              'chart_form': ChartFilterForm(request.POST),
                                              'chart': charts})
        else:
            return render(request, template, {'filter_form': filter_form,
                                              'chart_form': chart_filter_form,
                                              'result_count': 0})


