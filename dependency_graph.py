import networkx as nx
from DAG import *
import numpy as np


def initiate_dependency_graph(t):
    """
    Construct a dependency graph
    :param t: The number of transactions
    :return: A directed graph (networkx.DiGraph) where nodes are IDs.
    """
    nodes = set()  # To collect all unique node IDs

    # Extract all unique IDs
    nodes.update(range(t))

    nodes = list(nodes)  # Convert to a list for consistent indexing
    dependency_graph = nx.DiGraph()  # Create a directed graph
    dependency_graph.add_nodes_from(nodes)  # Add all nodes

    return dependency_graph



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
        nodes.update(set(ordering))

    # Calculate weights and add edges based on the criteria
    for i, node_a in enumerate(nodes):
        for j, node_b in enumerate(nodes):
            if i >= j or dependency_graph.has_edge(node_a, node_b) or dependency_graph.has_edge(node_b, node_a):
                continue  # Avoid duplicate pairs and self-comparison

            # Calculate Weight(A, B) and Weight(B, A)
            weight_ab = 0
            weight_ba = 0
            for order in local_orderings:
                if order[node_a] < order[node_b] or order[node_a] is not None and order[node_b] is None:
                    weight_ab += 1
                if order[node_b] < order[node_a] or order[node_b] is not None and order[node_a] is None:
                    weight_ba += 1

            if weight_ab > weight_ba or (weight_ab == weight_ba and node_a < node_b):
                if weight_ab >= threshold:
                    dependency_graph.add_edge(node_a, node_b)
            elif weight_ba > weight_ab:
                if weight_ba >= threshold:
                    dependency_graph.add_edge(node_b, node_a)


def find_hamiltonian_path(tournament_graph):
    """
    Finds a Hamiltonian path in a tournament graph.

    :param tournament_graph: A directed graph (networkx.DiGraph) representing a tournament.
    :return: A list of nodes representing the Hamiltonian path, or None if no path exists.
    """
    if not nx.is_directed(tournament_graph):
        raise ValueError("The graph must be a directed tournament.")

    nodes = list(tournament_graph.nodes())
    if len(nodes) < 2:
        return nodes  # A single node or empty graph trivially has a Hamiltonian path

    # Start with the first node as the initial path
    nodes.sort()
    # random.shuffle(nodes)
    path = [nodes[-1]]

    for node in nodes[-2::-1]:
        inserted = False
        # Insert the node in the correct position in the current path
        for i, current_node in enumerate(path):
            if tournament_graph.has_edge(node, current_node):  # If there's an edge node -> current_node
                path.insert(i, node)
                inserted = True
                break
        if not inserted:
            # If the node doesn't have an edge to any node in the current path, append it
            path.append(node)
    return path


def __test__():
    t = 5
    s = 100
    d = 1
    n = 4
    isThemis = False
    f = (n-1)//4 if isThemis else (n-1)//3
    distance = 1
    num_slot = 5
    is_leader_faulty = False
    deliver_based = True


    transactions = generate_transactions(t, s, d, n)
    transactions = sort_transactions_by_average_deliver_time(transactions)

    dag_vertices = initialize_dag_vertices(transactions, n, t, num_slot)
    find_and_update_causal_history(dag_vertices, num_slot, n)
    for current_round in range(0, num_slot, 2):
        for replica in range(n):
            leader_vertex = dag_vertices[replica][current_round]
            if leader_vertex.is_leader:
                print(replica, current_round, leader_vertex.causal_history)

    dg = initiate_dependency_graph(t)
    construct_dependency_graph(dg, dag_vertices, transactions, n, num_slot, f)
    # Create an adjacency matrix from the DiGraph
    adj_matrix = nx.to_numpy_array(dg, nodelist=sorted(G.nodes()))

    # Print the adjacency matrix
    print("\nAdjacency Matrix:")
    print(adj_matrix)

# __test__()

# for transaction in transactions:
#     print(transaction.ID, ":", transaction.average_deliver_time, transaction.deliver_time, transaction.deliver_ID)

