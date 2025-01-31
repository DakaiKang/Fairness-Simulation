from transactions import *

def Themis_update_positions(transactions, path):
    """
    Order transactions based on their assigned_timestamp and update their positions.

    :param transactions: List of Transaction objects.
    """
    transactions.sort(key=lambda x: x.ID)
    for idx, id in enumerate(path):
        transactions[id].pos = idx


def update_positions(transactions):
    """
    Order transactions based on their assigned_timestamp and update their positions.

    :param transactions: List of Transaction objects.
    """
    transactions.sort(key=lambda x: x.assigned_timestamp)
    for idx, transaction in enumerate(transactions):
        transaction.pos = idx


def DAG_update_positions(transactions):
    """
    Order transactions based on their assigned_timestamp and update their positions.

    :param transactions: List of Transaction objects.
    """
    transactions.sort(key=lambda x: x.DAG_assigned_timestamp)
    for idx, transaction in enumerate(transactions):
        transaction.DAG_pos = idx