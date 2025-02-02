from transactions import *
from collections import OrderedDict

def calculate_distance(txn1, txn2):
    count = 0
    for t1, t2 in zip(txn1.deliver_time, txn2.deliver_time):
        if t1 <= t2:
            count += 1
        elif t1 > t2:
            count -= 1
    return count

def calculate_distances(transactions):
    distances = dict()
    transactions.sort(key=lambda x: x.ID)
    for i in range(len(transactions)):
        for j in range(len(transactions)):
            if i == j:
                continue
            distances[(transactions[i].ID, transactions[j].ID)] = calculate_distance(transactions[i], transactions[j])

    return distances


def is_correct_pair(txn1, txn2, distances):
    if txn1.pos < txn2.pos and distances[(txn1.ID, txn2.ID)] > 0:
        return True
    if txn1.pos > txn2.pos and distances[(txn1.ID, txn2.ID)] < 0: 
        return True
    return False


def calculate_distances_correct_ratio(transactions, distances):
    total = dict()
    correct = dict()
    for i in range(len(transactions)):
        for j in range(i+1, len(transactions)):
            distance = distances[(transactions[i].ID, transactions[j].ID)]
            if distance < 0:
                distance = -distance
            if distance not in total:
                total[distance] = 0
                correct[distance] = 0
            total[distance] = total[distance] + 1
            if (is_correct_pair(transactions[i], transactions[j], distances)):
                correct[distance] = correct[distance] + 1
    for i in total:
        correct[i] = correct[i]/total[i]
    sorted_dict = OrderedDict(sorted(correct.items()))
    return sorted_dict