from transactions import *


def spearman_rank_correlation(x, y):
    """
    Compute Spearman's Rank Correlation Coefficient between two lists.

    :param x: First list of values.
    :param y: Second list of values.
    :return: Spearman's rank correlation coefficient.
    """
    if len(x) != len(y):
        raise ValueError("The two lists must have the same length.")

    # Rank the elements in x and y
    def rank_elements(values):
        sorted_indices = sorted(range(len(values)), key=lambda i: values[i])
        print(sorted_indices)
        ranks = [0] * len(values)
        for rank, index in enumerate(sorted_indices, start=1):
            ranks[index] = rank
        return ranks

    rank_x = rank_elements(x)
    rank_y = rank_elements(y)

    # print("rankx:", rank_x)
    # print(rank_y)

    # Compute Spearman's rank correlation
    n = len(x)
    d_squared_sum = sum((rank_x[i] - rank_y[i])**2 for i in range(n))
    spearman_rho = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))

    return spearman_rho


def correlation(transactions, deliver_based):
    if deliver_based:
        transactions.sort(key=lambda x: x.deliver_ID)
    else:
        transactions.sort(key=lambda x: x.ID)
    list_ = [transaction.ID for transaction in transactions]

    transactions.sort(key=lambda x: x.pos)
    list1 = [transaction.ID for transaction in transactions]
    # print(list)
    # print(list1)
    correlation = spearman_rank_correlation(list_, list1)
    return correlation