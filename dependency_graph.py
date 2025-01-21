from DAG import *
import networks as nx

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