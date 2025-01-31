from DAG import *
from transactions import *
from dependency_graph import *
from update_pos import *
from spearman import *

def update_dependency_graph(dependency_graph, local_orderings, threshold):
    """
    Update a dependency graph based on a set of local orderings.

    :param dependency_graph: An existing dependency graph with t nodes.
    :param local_orderings: A dictionary where keys are indices of local orderings (0 to x-1),
                            and values are mappings of IDs to indices in the sorted order.
    :param threshold: A threshold value for adding edges between nodes
    """

    nodes = set()  # To collect all unique node IDs

    # Extract all unique IDs
    for ordering in local_orderings:
        # print("ordering", ordering)
        nodes.update(set(ordering))

    # Calculate weights and add edges based on the criteria
    for i, node_a in enumerate(nodes):
        # print("i:", i, node_a)
        for j, node_b in enumerate(nodes):
            if i >= j or dependency_graph.has_edge(node_a, node_b) or dependency_graph.has_edge(node_b, node_a):
                continue  # Avoid duplicate pairs and self-comparison
            # Calculate Weight(A, B) and Weight(B, A)
            weight_ab = 0
            weight_ba = 0
            for order in local_orderings:
                if (node_a not in order) and (node_b not in order):
                    continue
                elif node_a not in order:
                    weight_ba += 1
                elif node_b not in order:
                    weight_ab += 1
                elif order[node_a] < order[node_b]:
                    weight_ab += 1
                elif order[node_b] < order[node_a]:
                    weight_ba += 1

            if weight_ab > weight_ba or (weight_ab == weight_ba and node_a < node_b):
                if weight_ab >= threshold:
                    dependency_graph.add_edge(node_a, node_b)
            elif weight_ba > weight_ab:
                if weight_ba >= threshold:
                    dependency_graph.add_edge(node_b, node_a)


def update_dependency_graph_with_causal_history(dependency_graph, leader_vertex, dag_vertices, n, threshold):
    """
    Process a leader vertex's causal history and add all deliver_times in the causal history
    to the useful_timestamps field of corresponding Transactions.

    :param leader_vertex: The leader DAGVertex whose causal history is being processed.
    :param dag_vertices: A 2D list of DAGVertex objects representing the DAG (n x 10 structure).
    """
    if not leader_vertex.is_leader:
        # print(f"Vertex {leader_vertex} is not a leader. Skipping.")
        return

    local_orderings = list()
    local_orderings_dict = {}
    for i in range(n):
        local_orderings_dict[i] = dict()

    # Iterate over all vertices in the causal history
    for replica, round_number in leader_vertex.causal_history:
        dag_vertex = dag_vertices[replica][round_number]  # Resolve the DAGVertex
        local_orderings_dict[replica][round_number] = dag_vertex.id_time_pairs

    for i in range(n):
        idx = 1
        local_ordering = dict()
        round_number_list = sorted(local_orderings_dict[i].keys())
        # print("round_number_list", round_number_list)
        for round_number in round_number_list:
            id_time_pairs = local_orderings_dict[i][round_number]
            for x in id_time_pairs:
                local_ordering[x[0]] = idx
                idx += 1
        local_orderings.append(local_ordering)

    update_dependency_graph(dependency_graph, local_orderings, threshold)

    # print(f"Processed causal history for leader vertex: {leader_vertex}")


def construct_dependency_graph(dependency_graph, dag_vertices, transactions, n, num_slot, f):
    """
        For every leader vertex in round-ascending order:
        1. Process the leader's causal history and update the `useful_timestamps` of transactions.
        2. Calculate the `DAG_assigned_timestamp` for transactions with at least 2f+1 `useful_timestamps`.

        :param dag_vertices: A 2D list of DAGVertex objects representing the DAG (n x 10 structure).
        :param transactions: A list of Transaction objects.
        :param n: The total number of processes (used to calculate f).
        """
    # Iterate through rounds in ascending order
    for round in range(0, num_slot - 1, 2):
        for i in range(n):
            leader_vertex = dag_vertices[i][round]
            if leader_vertex.is_leader:
                # print(f"Processing leader at round {leader_vertex.round}: {leader_vertex}")

                # Process causal history of the leader
                update_dependency_graph_with_causal_history(dependency_graph, leader_vertex, dag_vertices, n, f+1)

                # print(f"Finished processing leader at round {leader_vertex.round}")

    leader_vertex = DAGVertex(is_leader=True, round=num_slot)
    for i in range(n):
        for j in range(num_slot):
            leader_vertex.causal_history.add((i, j))
    # print(f"Processing leader at round {leader_vertex.round}: {leader_vertex}")

    # Process causal history of the leader
    update_dependency_graph_with_causal_history(dependency_graph, leader_vertex, dag_vertices, n, (n-f)//2)

    # print(f"Finished processing leader at round {leader_vertex.round}")



def __test__():
    t = 1000
    s = 1
    d = 100
    n = 4
    isThemis = True
    f = (n-1)//4 if isThemis else (n-1)//3
    distance = 1
    num_slot = 5
    is_leader_faulty = False
    deliver_based = True


    transactions = generate_transactions(t, s, d, n)
    transactions = sort_transactions_by_average_deliver_time(transactions)
    local_orderings = generate_local_orderings(transactions, n)
    # update_transaction_deliver_times(transactions, t, n, s, d, num_slot, f)
    dag_vertices = initialize_dag_vertices(transactions, n, t, num_slot)
    find_and_update_causal_history(dag_vertices, num_slot, n)
    for current_round in range(0, num_slot, 2):
        for replica in range(n):
            leader_vertex = dag_vertices[replica][current_round]
            if leader_vertex.is_leader:
                print(replica, current_round, leader_vertex.causal_history)

    dg = initiate_dependency_graph(t)
    if isThemis:
        update_dependency_graph(dg, local_orderings[:n-2*f], f+1)
    else:
        construct_dependency_graph(dg, dag_vertices, transactions, n, num_slot, f)
    # Create an adjacency matrix from the DiGraph
    adj_matrix = nx.to_numpy_array(dg, nodelist=sorted(dg.nodes()))

    path = find_hamiltonian_path(dg)
    Themis_update_positions(transactions, path)

    transactions.sort(key=lambda x: x.ID)
    for transaction in transactions:
        print(transaction.ID, transaction.average_deliver_time)
    # Print the adjacency matrix
    print("\nAdjacency Matrix:")
    print(adj_matrix)
    print("path", path)

    print(correlation(transactions, deliver_based))

# __test__()