from django import forms
from transactions.charts import Chart
from transactions.models import Transaction
from transactions.templatetags.transaction_template_tags import camelcase

HOUSE_TYPE_CHOICES = (
    ('', 'All'),
    ('h', 'HDB'),
    ('c', 'Condo'),
)

ROOM_CHOICES = [('', 'All')] + [(str(i), str(i)) for i in range(1, 9)] + [('u', 'Unknown')]


class ChartFilterForm(forms.Form):
    """
    A form to customize chart series and the transaction list to be display
    """
    series = forms.MultipleChoiceField(label="Chart Series", required=False,
                                       widget=forms.CheckboxSelectMultiple,
                                       choices=Chart.CHART_SERIES_CHOICES,
                                       initial=[Chart.ITSELF])
    list = forms.ChoiceField(label="List", required=False,
                             choices=Chart.LIST_CHOICES,
                             initial=Chart.ITSELF)

    def __init__(self, *args, **kwargs):
        super(ChartFilterForm, self).__init__(*args, **kwargs)

    def get_one_property(self):
        """
        Return True if the FilterForm(below) need to result in exactly 1 property. Otherwise return False.
        """
        self.is_valid()  # Call it in order to be able to call self.cleaned_data
        if self.cleaned_data['list'] != Chart.ITSELF:
            return True
        if Chart.NEIGHBOR_ADDRESS in self.cleaned_data['series']:
            return True
        if Chart.NEIGHBOR_POSTALCODE in self.cleaned_data['series']:
            return True
        return False


class FilterForm(forms.Form):
    type = forms.ChoiceField(label="Type", choices=HOUSE_TYPE_CHOICES, required=False)
    name = forms.CharField(label="HouseName", widget=forms.TextInput(), required=False)
    postal_code = forms.CharField(label="PostalCode", widget=forms.TextInput(), required=False)
    address = forms.CharField(label="Address", widget=forms.TextInput(), required=False)
    room_count = forms.ChoiceField(label="No.Bedroom", choices=ROOM_CHOICES, required=False)

    def __init__(self, *args, **kwargs):
        self.one_property = kwargs.pop('one_property', None)
        super(FilterForm, self).__init__(*args, **kwargs)
        self.property = None
        self.transactions = None

    def clean(self):
        """
        Clean form fields and calculate filter transactions.
        Check validity of the form. If the form is invalid, raise Validation Error

        If Chart Series or List has Neighbor Postal Code or Neighbor Address selected,
        The filtered transactions should contain exactly 1 property

        """
        # clean all fields. If a field value is empty, make it become None
        for field in self.fields:
            if self.cleaned_data[field] == "":
                self.cleaned_data[field] = None

        # refine text fields with camelcase
        self.cleaned_data['name'] = camelcase(self.cleaned_data['name'])
        self.cleaned_data['address'] = camelcase(self.cleaned_data['address'])

        # get filtered transactions
        self.transactions = Transaction.get_transactions(type=self.cleaned_data['type'],
                                                         name=self.cleaned_data['name'],
                                                         postal_code=self.cleaned_data['postal_code'],
                                                         address=self.cleaned_data['address'],
                                                         room_count=self.cleaned_data['room_count'])

        if self.one_property:  # If the form should return 1 property

            # If transactions is empty, raise Validation Error
            if len(self.transactions) == 0:
                raise forms.ValidationError("Error: No transaction match!")

            # If transactions contain more than 1 property, raise Validation Error
            temp = self.transactions.filter(address=self.transactions[0].address).filter(postal_code=self.transactions[0].postal_code)
            if len(temp) != len(self.transactions):
                # transactions contain more than 1 property, raise ValidationError
                raise forms.ValidationError("Error: More than 1 property match! If you select 'neighbor postalcode' or 'neighbor coordinate', please make sure the query returns exactly 1 property.")

            self.property = self.transactions[0]

        return self.cleaned_data

    def get_property(self):
        return self.property

    def get_transactions(self):
        return self.transactions
