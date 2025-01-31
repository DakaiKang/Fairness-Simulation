from DAG import *
from transactions import *
from dependency_graph import *
from update_pos import *
from spearman import *
from RL import *
from distance import *


def Run_Themis(dg, n, t, s, d, num_slot, transactions, deliver_based, is_leader_faulty):
    f = (n-1)//4

    if is_leader_faulty:
        update_transaction_deliver_times(transactions, t, n, s, d, num_slot, (n-1)//4)
    local_orderings = generate_local_orderings(transactions, n)

    update_dependency_graph(dg, local_orderings[:n-2*f], f+1)
    adj_matrix = nx.to_numpy_array(dg, nodelist=sorted(dg.nodes()))

    path = find_hamiltonian_path(dg)
    Themis_update_positions(transactions, path)

    # transactions.sort(key=lambda x: x.ID)
    # for transaction in transactions:
    #     print(transaction.ID, transaction.average_deliver_time)
    # Print the adjacency matrix
    # print("\nAdjacency Matrix:")
    # print(adj_matrix)
    print("Themis Path: ", path)
    return correlation(transactions, deliver_based)
    


def Run_FairDAG_RL(dg, transactions, n, t, s, d, num_slot, deliver_based, is_leader_faulty):
    f = (n-1)//3

    if is_leader_faulty:
        update_transaction_deliver_times(transactions, t, n, s, d, num_slot, (n-1)//3)

    dag_vertices = initialize_dag_vertices(transactions, n, t, num_slot)
    find_and_update_causal_history(dag_vertices, num_slot, n)
    for current_round in range(0, num_slot, 2):
        for replica in range(n):
            leader_vertex = dag_vertices[replica][current_round]

    construct_dependency_graph(dg, dag_vertices, transactions, n, num_slot, f)
    adj_matrix = nx.to_numpy_array(dg, nodelist=sorted(dg.nodes()))

    path = find_hamiltonian_path(dg)
    Themis_update_positions(transactions, path)

    # transactions.sort(key=lambda x: x.ID)
    # for transaction in transactions:
    #     print(transaction.ID, transaction.average_deliver_time)
    # Print the adjacency matrix
    # print("\nAdjacency Matrix:")
    # print(adj_matrix)
    print("FairDAG_RL Path: ", path)
    return correlation(transactions, deliver_based)


def RL_Fairness_Test():
    t = 20
    s = 1
    d = 10
    n = 49
    isThemis = True
    distance = 1
    num_slot = 5
    is_leader_faulty = False
    deliver_based = True

    transactions = generate_transactions(t, s, d, n)
    transactions = sort_transactions_by_average_deliver_time(transactions)
    distances = calculate_distances(transactions)
    print(distances)

    # value1 = Run_Themis(initiate_dependency_graph(t), n, t, s, d, num_slot, transactions, deliver_based, is_leader_faulty)
    # value2 = Run_FairDAG_RL(initiate_dependency_graph(t), transactions, n, t, s, d, num_slot, deliver_based, is_leader_faulty)
    # print("Themis Correlation: ", value1)
    # print("FairDAG_RL Correlation: ", value2)

RL_Fairness_Test()