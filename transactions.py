import statistics
import random

class Transaction:
    def __init__(self, ID, send_time, deliver_time=None, receive_time=None, assigned_timestamp=None, num_correct=0, pos=None,
                 DAG_assigned_timestamp=None, useful_timestamps=None, DAG_num_correct=0, DAG_pos=None):
        """
        Initialize a Transaction object.

        :param ID: Unique identifier for the transaction (str or int).
        :param send_time: Time when the transaction was sent.
        :param deliver_time: List of times when the transaction was delivered (list).
        :param deliver_time: List of times when the deliver_times were received by the proposer (list).
        :param assigned_timestamp: Time when the transaction was assigned (optional).
        :param num_correct: Number of correct events (default: 0).
        :param pos: Position of the transaction in a sorted list (default: None).
        :param DAG_assigned_timestamp: Timestamp associated with the DAG context (optional).
        :param useful_timestamps: List of useful timestamps associated with the transaction (default: empty list).
        :param DAG_num_correct: Number of correct events within the DAG (default: 0).
        :param DAG_pos: Position of the transaction within the DAG (default: None).
        """
        self.ID = ID
        self.send_time = send_time
        self.deliver_time = deliver_time if deliver_time is not None else []
        self.receive_time = receive_time if receive_time is not None else []
        self.assigned_timestamp = assigned_timestamp
        self.num_correct = num_correct
        self.pos = pos
        self.DAG_assigned_timestamp = DAG_assigned_timestamp
        self.useful_timestamps = useful_timestamps if useful_timestamps is not None else set()
        self.DAG_num_correct = DAG_num_correct  # New field for DAG-related correctness
        self.DAG_pos = DAG_pos  # New field for DAG position
        self.average_deliver_time = statistics.mean(deliver_time)
        self.deliver_ID = ID

    def __repr__(self):
        """Return a string representation of the Transaction object."""
        return (f"Transaction(ID={self.ID}, send_time={self.send_time}, "
                f"deliver_time={self.deliver_time}, assigned_timestamp={self.assigned_timestamp}, "
                f"num_correct={self.num_correct}, pos={self.pos}, "
                f"DAG_assigned_timestamp={self.DAG_assigned_timestamp}, "
                f"useful_timestamps={self.useful_timestamps}, "
                f"DAG_num_correct={self.DAG_num_correct}, DAG_pos={self.DAG_pos})")


def sort_transactions_by_average_deliver_time(transactions):
    """
    Sort a list of transactions based on their average deliver time and update their deliver_ID
    based on their indices in the sorted list.

    :param transactions: List of Transaction objects.
    """
    # Sort transactions by average_deliver_time
    sorted_transactions = sorted(transactions, key=lambda tx: tx.average_deliver_time)

    # Update deliver_ID based on the sorted order
    for index, transaction in enumerate(sorted_transactions):
        transaction.deliver_ID = index + 1

    return sorted_transactions


def generate_transactions(t, s, d, n):
    """
    Generate a list of transactions.

    :param t: Number of transactions to generate.
    :param s: Multiplier for send_time.
    :param d: Mean delay for exponential distribution.
    :param n: Number of deliver_time entries for each transaction.
    :return: List of Transaction objects.
    """
    transactions = []
    for ID in range(t):
        send_time = s * ID
        deliver_time = [send_time + random.expovariate(1 / d) for _ in range(n)]

        receive_time = [dt + random.expovariate(1 / d) for dt in deliver_time]
        transaction = Transaction(ID=ID, send_time=send_time, deliver_time=deliver_time, receive_time=receive_time)
        transactions.append(transaction)
    return transactions


def print_transactions(transactions):
    """
    Print a list of transactions.

    :param transactions: List of Transaction objects.
    """
    for transaction in transactions:
        print(transaction)


def update_transaction_deliver_times(transactions, t, n, s, d, num_slot, f):
    """
    Update the first f values of deliver_time for each transaction.

    :param transactions: A list of Transaction objects.
    :param n: The total number of processes (used to calculate f).
    :param s: The multiplier for send_time.
    :param d: The base delay value to add.
    """

    for transaction in transactions:
        for i in range(f):  # Ensure not to exceed available deliver_time entries
            transaction.deliver_time[i] = d + s * (t - transaction.deliver_ID)

    print("Updated deliver_time[0:f] for all transactions.")



def generate_local_orderings(transactions, n):
    """
    Generate local orderings by sorting all transactions based on deliver_time[i] for i from 0 to n-1.
    Return a dictionary mapping ID to index in the sorted transactions for each i.

    :param transactions: A list of Transaction objects.
    :param n: The number of indices to consider in deliver_time.
    :return: A dictionary where keys are indices i, and values are mappings of ID to index in the sorted list.
    """
    local_orderings = []

    for i in range(n):
        # Ensure i is within the valid range of deliver_time indices for all transactions
        for txn in transactions:
            if i >= len(txn.deliver_time):
                raise ValueError(f"Index {i} is out of range for deliver_time in transaction ID {txn.ID}.")

        # Sort transactions based on the i-th deliver_time
        sorted_transactions = sorted(transactions, key=lambda txn: txn.deliver_time[i])

        # Create a dictionary mapping ID to index for this deliver_time[i]
        local_orderings.append({txn.ID: idx for idx, txn in enumerate(sorted_transactions)})

    return local_orderings


def __test__():
    t = 1000
    s = 1
    d = 100
    n = 97
    isThemis = False
    f = (n-1)//4 if isThemis else (n-1)//3
    distance = 1
    num_slot = 5
    is_leader_faulty = True
    deliver_based = True


    transactions = generate_transactions(t, s, d, n)
    transactions = sort_transactions_by_average_deliver_time(transactions)
    update_transaction_deliver_times(transactions, t, n, s, d, num_slot, f)

    for transaction in transactions:
        print(transaction.ID, ":", transaction.average_deliver_time, transaction.deliver_time, transaction.deliver_ID)

# __test__()

