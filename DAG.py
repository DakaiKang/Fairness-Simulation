import random
from transactions import *

class DAGVertex:
    def __init__(self, id_time_pairs = None, strong_edges = None, is_leader=False, round=0, replica = 0):
        """
        Initialize a DAGVertex object.

        :param id_time_pairs: List of (ID, deliver_time) pairs.
        :param strong_edges: List of indices representing strong edges to other vertices.
        :param is_leader: Boolean indicating if this vertex is a leader.
        :param round: The round number for this vertex.
        """
        self.id_time_pairs = id_time_pairs
        self.strong_edges = strong_edges
        self.is_leader = is_leader
        self.round = round
        self.replica = replica
        self.causal_history = set()  # New field to store the causal history of the vertex


    def __repr__(self):
        """Return a string representation of the DAGVertex object."""
        return (f"DAGVertex(id_time_pairs={self.id_time_pairs}, strong_edges={self.strong_edges}, "
                f"is_leader={self.is_leader}, round={self.round}, "
                f"causal_history={[v for v in self.causal_history]})")



def initialize_dag_vertices(transactions, n, t, num_slot):
    """
    Initialize n * 10 DAGVertex objects.

    :param transactions: List of Transaction objects.
    :param n: Number of groups for the DAG vertices.
    :param t: Total number of transactions.
    :return: A 2D list of DAGVertex objects with dimensions n * 10.
    """
    # Initialize the 2D list to store DAGVertex objects
    dag_vertices = [[DAGVertex() for _ in range(num_slot)] for _ in range(n)]

    # Calculate f and 2f+1
    f = (n - 1) // 3

    # Loop over each group
    for i in range(n):
        # Extract all deliver_times[i] from the transactions
        deliver_times_with_ids = [(txn.ID, txn.deliver_time[i]) for txn in transactions]

        # Sort by deliver_time in ascending order
        deliver_times_with_ids.sort(key=lambda x: x[1])

        # Divide into 10 subgroups
        for j in range(num_slot):
            # Calculate the start and end indices for this subgroup
            start_idx = j * (t // num_slot)
            end_idx = (j + 1) * (t // num_slot)

            # Extract id_time_pairs for this vertex
            id_time_pairs = deliver_times_with_ids[start_idx:end_idx]

            # Select 2f+1 random strong edges
            strong_edges = random.sample(range(n), 2*f+1)

            # Create the DAGVertex with the corresponding id_time_pairs
            dag_vertices[i][j] = DAGVertex(id_time_pairs=id_time_pairs, round=j, strong_edges=strong_edges, replica=i)

    for j in range(num_slot):
        # If it's an even round, randomly select a leader vertex
        if j % 2 == 0:
            leader_idx = random.choice(range(n))  # Randomly select one vertex in the group
            print("random:", leader_idx, j)
            dag_vertices[leader_idx][j].is_leader = True
    return dag_vertices


def find_and_update_causal_history(dag_vertices, num_slot, n):
    """
    Find and update the causal history of the leader vertices in a DAG.

    :param dag_vertices: A 2D list of DAGVertex objects representing the DAG (n x 10 structure).
    """
    for current_round in range(0, num_slot, 2):
        for replica in range(n):
            leader_vertex = dag_vertices[replica][current_round]
            if leader_vertex.is_leader:
                print(f"Processing leader vertex: {leader_vertex}")

                # Initialize the causal history with the leader itself
                leader_vertex.causal_history.add((leader_vertex.replica, leader_vertex.round))
                stack = [(leader_vertex.replica, leader_vertex.round)]  # Stack for DFS traversal

                while stack:
                    # Get the current vertex
                    current_vertex_index = stack.pop()
                    current_vertex = dag_vertices[current_vertex_index[0]][current_vertex_index[1]]

                    # Traverse strong edges to find connected vertices
                    if current_vertex.round > 0:
                        for edge in current_vertex.strong_edges:
                            # Add connected vertices to the causal history
                            next_vertex = (edge, current_vertex.round - 1)
                            if next_vertex not in leader_vertex.causal_history:
                                leader_vertex.causal_history.add(next_vertex)
                                stack.append(next_vertex)


def __test__():
    t = 1000
    s = 1
    d = 100
    n = 4
    isThemis = False
    f = (n-1)//4 if isThemis else (n-1)//3
    distance = 1
    num_slot = 5
    is_leader_faulty = True
    deliver_based = True


    transactions = generate_transactions(t, s, d, n)
    transactions = sort_transactions_by_average_deliver_time(transactions)
    update_transaction_deliver_times(transactions, t, n, s, d, num_slot, f)
    dag_vertices = initialize_dag_vertices(transactions, n, t, num_slot)
    find_and_update_causal_history(dag_vertices, num_slot, n)
    for current_round in range(0, num_slot, 2):
        for replica in range(n):
            leader_vertex = dag_vertices[replica][current_round]
            if leader_vertex.is_leader:
                print(replica, current_round, leader_vertex.causal_history)



__test__()

# for transaction in transactions:
#     print(transaction.ID, ":", transaction.average_deliver_time, transaction.deliver_time, transaction.deliver_ID)

