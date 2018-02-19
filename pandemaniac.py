import sim
import json
import numpy as np
import networkx as nx
import operator
import sys
from heapq import nlargest
from networkx.algorithms.approximation import min_weighted_vertex_cover
# testgraph1.json has 500 nodes
# testgraph2.json has 1000 nodes

def main():
    ''' Main function: Gets user input and creates necessary output files
    '''
    filename, num_seeds, strategies = get_user_input()
    GRAPH_FILENAME = filename + ".json"

    G = load_graph(GRAPH_FILENAME)
    NUM_ITERATIONS = 50
    for s in strategies:
        strategy = s.lower()
        if strategy == 'r':
            output = random_strategy(G, NUM_ITERATIONS, num_seeds) 
        elif strategy == 'd':   
            output = degree_centrality_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'e':
            output = eigenvector_centrality_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'b':
            output = betweenness_centrality_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'c':
            output = clustering_coefficient_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'k':
            output = katz_centrality_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'm':
            output = mst_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 's':
            output = dominating_set_strategy(G, NUM_ITERATIONS, num_seeds)
        elif strategy == 'v':
            output = vertex_cover_strategy(G, NUM_ITERATIONS, num_seeds)
        else:
            assert(False)
        raw_file = GRAPH_FILENAME[:-5] # Take out the .json extension
        output_filename = raw_file + "_" + strategy + '.txt'
        output_list(output_filename, output)
        print(strategy + " successfully generated.")
    return

def get_user_input():
    ''' Gets user input for name of graph and strategies to run
    where the strategies are:
    R/r: Random
    D/d: Degree centrality
    B/b: Betweenness centrality
    K/k: Katz centrality
    E/e: Eigenvector centrality
    C/c: Clustering coefficient
    M/m: Minimum spanning tree
    S/s: Dominating set
    V/v : Vertex cover

    Also extrapolates the num_seeds from the name of the graph

    Arguments: n/a
    Returns:   name of graph, number of seeds, list of strategies
    '''
    filename = raw_input("Enter the filename (leave out .json extension) -> ")
    # INPUT FILE IS OF FORM x.y.z
    # where x is number of players, y is the number of seeds, z is ID # for graph
    filename_split = filename.strip().split('.')
    assert(len(filename_split) == 3)
    num_seeds = filename_split[1]
    strategy_str = raw_input("Enter the strategies to run separated by spaces -> ")
    strategy_lst = strategy_str.strip().split()

    return filename, int(num_seeds), strategy_lst

def load_graph(filename):
    ''' Loads in the graph.

    Args:
        filename -- the file from which to read adjacency list from

    Returns:
        a networkx graph
    '''
    with open(filename, 'r') as fr:
        graph = json.load(fr)
    
    # graph is now the data in the file stored as a dictionary
    # with each key as a node, and the values as a list of
    # adjacent nodes

    # Create an undirected graph
    G = nx.Graph(graph)
    return G

def vertex_cover_strategy(G, num_iterations, num_seeds):
    ''' Picks top degreed nodes from vertex cover (VC) of 
    input graph. If there are less nodes in the VC than 
    num_seeds, then we pick from top degreed nodes of the 
    input graph.

    Given an undirected graph G = (V, E) and a function w 
    assigning nonnegative weights to its vertices, 
    find a minimum weight subset of V such that each edge in E is 
    incident to at least one vertex in the subset.
    
    Note: every vertex cover is a dominating set, but not every
    dominating set is a vertex cover

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on VC strategy
    '''

    vc_nodes = min_weighted_vertex_cover(G)
    nodes_to_remove = G.nodes() - vc_nodes
    subgraph = G.copy()
    subgraph.remove_nodes_from(nodes_to_remove)
    number_of_nodes = num_seeds
    if len(vc_nodes) < num_seeds:
        number_of_nodes = len(vc_nodes)
    centralities_dict = nx.degree_centrality(subgraph)
    sorted_centralities = nlargest(number_of_nodes, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]

    nodes_top_degrees = degree_centrality_strategy(G, 1, num_seeds)
    # In case we need more seed nodes, we simply pull from the top degreed nodes of the input graph
    i = 0
    while (len(node_keys) != num_seeds):
        if nodes_top_degrees[i] not in node_keys:
            node_keys.append(nodes_top_degrees[i])
        i += 1
    assert(len(node_keys) == num_seeds)
    return node_keys * num_iterations

def dominating_set_strategy(G, num_iterations, num_seeds):
    ''' Picks top degreed nodes from dominating set(ds) of 
    input graph. If there are less nodes in the ds than 
    num_seeds, then we pick from top degreed nodes of the 
    input graph.

    A dominating set for a graph G = (V, E) is a node subset 
    D of V such that every node not in D is adjacent to at least 
    one member of D.

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on DS strategy
    '''

    ds_nodes = nx.dominating_set(G)
    nodes_to_remove = G.nodes() - ds_nodes
    subgraph = G.copy()
    subgraph.remove_nodes_from(nodes_to_remove)
    assert(len(G.nodes()) > len(subgraph.nodes()))
    number_of_nodes = num_seeds
    if len(ds_nodes) < num_seeds:
        number_of_nodes = len(ds_nodes)
    centralities_dict = nx.degree_centrality(subgraph)
    sorted_centralities = nlargest(number_of_nodes, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]

    nodes_top_degrees = degree_centrality_strategy(G, 1, num_seeds)
    # In case we need more seed nodes, we simply pull from the top degreed nodes of the input graph
    i = 0
    while (len(node_keys) != num_seeds):
        if nodes_top_degrees[i] not in node_keys:
            node_keys.append(nodes_top_degrees[i])
        i += 1
    assert(len(node_keys) == num_seeds)
    return node_keys * num_iterations

def mst_strategy(G, num_iterations, num_seeds):
    ''' Picks top degreed nodes from MST of input graph.
    If there are less nodes in the MST than num_seeds, 
    then we pick from top degreed nodes of the input graph

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on MST
    '''

    mst = nx.minimum_spanning_tree(G)
    number_of_nodes = num_seeds
    if len(mst) < num_seeds:
        number_of_nodes = len(mst)
    centralities_dict = nx.degree_centrality(mst)
    sorted_centralities = nlargest(number_of_nodes, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]

    nodes_top_degrees = degree_centrality_strategy(G, 1, num_seeds)
    # In case we need more seed nodes, we simply pull from the top degreed nodes of the input graph
    i = 0
    while (len(node_keys) != num_seeds):
        if nodes_top_degrees[i] not in node_keys:
            node_keys.append(nodes_top_degrees[i])
        i += 1
    assert(len(node_keys) == num_seeds)
    return node_keys * num_iterations

def clustering_coefficient_strategy(G, num_iterations, num_seeds):
    ''' Picks the top nodes based on clustering coefficient

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on clustering coefficients
    '''

    clustering_dict = nx.clustering(G)
    sorted_clustering_nodes = nlargest(num_seeds, clustering_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_clustering_nodes]
    return node_keys * num_iterations

def eigenvector_centrality_strategy(G, num_iterations, num_seeds):
    ''' Picks the top nodes based on eigenvector centrality

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the eigenvector centrality
    '''

    centralities_dict = nx.eigenvector_centrality(G)
    sorted_centralities = nlargest(num_seeds, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]
    return node_keys * num_iterations

def katz_centrality_strategy(G, num_iterations, num_seeds):
    ''' Picks the top nodes based on eigenvector centrality

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the katz centrality
    '''

    centralities_dict = nx.katz_centrality(G)
    sorted_centralities = nlargest(num_seeds, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]
    return node_keys * num_iterations

def degree_centrality_strategy(G, num_iterations, num_seeds):
    ''' Picks the top nodes based on degree centrality

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the degree centrality
    '''

    centralities_dict = nx.degree_centrality(G)
    sorted_centralities = nlargest(num_seeds, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]
    return node_keys * num_iterations

def random_strategy(G, num_iterations, num_seeds):
    ''' Basic strategy of picking random nodes 

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the random strategy
    '''

    # The output file should contain (num_seeds * num_iterations) lines
    all_seed_values = []
    for i in range(num_iterations):
        seed_values = np.random.choice(len(G), num_seeds, 
            replace=False).tolist()
        all_seed_values.extend(seed_values)
    #assert(len(all_seed_values) == num_seeds * num_iterations)
    return all_seed_values

def betweenness_centrality_strategy(G, num_iterations, num_seeds):
    ''' Picks the top nodes based on betweenness centrality

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the betweenness centrality
    '''

    centralities_dict = nx.betweenness_centrality(G)
    sorted_centralities = nlargest(num_seeds, centralities_dict.items(), key=operator.itemgetter(1))
    node_keys = [i[0] for i in sorted_centralities]
    return node_keys * num_iterations

def random_strategy(G, num_iterations, num_seeds):
    ''' Basic strategy of picking random nodes 

    Args:
        G --                the input graph
        num_iterations --   the number of rounds
        num_seeds --        the number of seed nodes to select

    Returns: list of output nodes based on the random strategy
    '''

    # The output file should contain (num_seeds * num_iterations) lines
    all_seed_values = []
    for i in range(num_iterations):
        seed_values = np.random.choice(len(G), num_seeds, 
            replace=False).tolist()
        all_seed_values.extend(seed_values)
    return all_seed_values

def output_list(filename, seed_values):
    ''' Writes the given seed values to an output file for submisson

    Args:
        filename --         the filename of the file for which the values go into
        seed_values --      list of seed_values to write (one per line)
    
    Returns: n/a
    '''
    with open(filename, 'w') as fw:
        fw.write("\n".join(map(str, seed_values)))
    return

main()

