from transactions.models import Transaction


def get_transactions_by_property(transactions=Transaction.objects.all(),
                                 property=None):
    """
    Get a list of transactions with property=specified property
    Get from an original list

    :param transactions: original list of transactions
    :param property: specified property
    :return: a list of transactions (can be empty)
    """
    transaction_list = [trans for trans in transactions if is_same_property(trans, property)]
    return transaction_list


def get_transactions_by_neighbor_postal_code(transactions=Transaction.objects.all(),
                                             postal_code=None):
    """
    Get a list of transactions whose postal_code is a neighbor of specified postal_code
    Get from an original list of transactions
    Two postal_code is neighbor if they differs only the last digit

    :param transactions: original list of transaction
    :param postal_code: specified postal_code
    :return: if postal_code is not None, return a list of transaction, otherwise return an empty list
    """
    if postal_code is None:
        return []
    postal_code = postal_code[:len(postal_code) - 1]
    transaction_list = [trans for trans in transactions if trans.postal_code and trans.postal_code.startswith(postal_code)]
    return transaction_list


def get_transactions_by_neighbor_coordinate_property(transactions=Transaction.objects.all(),
                                                     property=None,
                                                     include=False):
    """
    Get a list of transactions whose is a co-ordinate neighbor of the specified transaction property.
    Get from an original list of transactions
    :param transactions: original list
    :param property: specified property
    :param include: include=False, ignore transactions with same property to specified property
    :return: If transaction is not None, return a list of transactions (can be empty)
    """

    if transactions is None:
        return []

    if include:
        transaction_list = [trans for trans in transactions if is_coordinate_neighbor(trans, property)]
    else:
        transaction_list = [trans for trans in transactions if not is_same_property(trans, property)
                            and is_coordinate_neighbor(trans, property)]
    return transaction_list


def weighted_avg_price(price_by_addr, price_by_neighbor_addr):
        if not price_by_addr:
            return price_by_neighbor_addr
        elif not price_by_neighbor_addr:
            return price_by_addr
        else:
            return 0.8 * price_by_addr + 0.2 * price_by_neighbor_addr


def is_coordinate_neighbor(trans1, trans2):
    return (abs(trans1.latitude - trans2.latitude) <= 0.005) \
        and (abs(trans1.longitude - trans2.longitude) <= 0.005)


def is_same_property(trans1, trans2):
    """
        Return True if trans1 & trans2 have same address + postal_code
    """
    return trans1.address == trans2.address and (trans1.postal_code == trans2.postal_code or not trans1.postal_code or not trans2.postal_code)
