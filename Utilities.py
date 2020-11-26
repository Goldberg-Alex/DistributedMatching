import copy
import itertools
import random
from typing import List

import networkx as nx

import Settings
from AgentBase import AgentBase, MatchingSolution

import matplotlib.pyplot as plt


def calculate_agent_matching_value(matching_solution: MatchingSolution, matching_graph) -> int:
    score = sum(matching_graph.get_edge_data(*edge)['weight'] for edge in matching_solution)

    return score


def calc_matching_score(agents: List[AgentBase], matching_graph: nx.Graph) -> float:
    matching_score_sum = 0.0

    for agent in agents:
        matching_score_sum += calculate_agent_matching_value(agent.get_solution(), matching_graph)
    average_matching_score = matching_score_sum / len(agents)
    return average_matching_score


def calculate_average_discrepancy(agents: List[AgentBase]) -> float:
    discrepancies_sum = 0.0
    agent_pairs_num = 0

    for first_agent, second_agent in list(itertools.combinations(agents, 2)):
        if first_agent == second_agent:
            continue

        discrepancies_sum += calculate_discrepancy_score(first_agent.get_solution(),
                                                         second_agent.get_solution())
        agent_pairs_num += 1

    return discrepancies_sum / agent_pairs_num


def calculate_discrepancy_score(first_solution: MatchingSolution, second_solution: MatchingSolution) -> int:
    sorted_first_solution = set((edge[0], edge[1]) if edge[0] > edge[1] else (edge[1], edge[0])
                                for edge in first_solution)

    sorted_second_solution = set((edge[0], edge[1]) if edge[0] > edge[1] else (edge[1], edge[0])
                                 for edge in second_solution)
    solutions_intersection = sorted_first_solution.intersection(sorted_second_solution)

    discrepancy = max(len(sorted_first_solution), len(sorted_second_solution)) - len(solutions_intersection)

    return discrepancy


do_once_full_graph = True
do_once_subgraph = True

def generate_matching_sub_graphs(matching_graph) -> List[nx.Graph]:
    zeroes_subgraph = matching_graph.copy()

    for edge in zeroes_subgraph.edges(data=True):
        edge[2]['weight'] = 0

    validated = False
    while not validated:
        sub_graphs = []
        for _ in range(Settings.NUM_AGENTS):
            sub_graph = zeroes_subgraph.copy()
            num_passed_edges = int(len(matching_graph.edges()) * Settings.PROPORTION_OF_EDGES_PER_SUBGRAPH)
            edge_list = list(matching_graph.edges(data=True))
            random.shuffle(edge_list)
            edge_list = edge_list[0:num_passed_edges]

            for source_edge in edge_list:
                sub_graph[source_edge[0]][source_edge[1]]['weight'] = source_edge[2]['weight']

            sub_graphs.append(sub_graph)

        # validate results:
        reassembled_matching = zeroes_subgraph.copy()

        for graph in sub_graphs:
            for edge in graph.edges(data=True):
                if edge[2]['weight'] > 0:
                    reassembled_matching.get_edge_data(*edge)['weight'] = edge[2]['weight']

        validated = True
        for edge in reassembled_matching.edges(data=True):
            if edge[2]['weight'] == 0:
                validated = False
                break

    global do_once_subgraph
    if do_once_subgraph:
        for sub_graph in sub_graphs:
            subgraph_copy = copy.deepcopy(sub_graph)
            if do_once_subgraph:
                for edge in sub_graph.edges():
                    edge_weight = sub_graph.get_edge_data(*edge)['weight']
                    if edge_weight < 1:
                        subgraph_copy.remove_edge(*edge)

                draw_bipartite_graph(subgraph_copy)
            do_once_subgraph = False

    return sub_graphs


def generate_connectivity_graph() -> nx.Graph:
    connected = False
    connectivity_graph = None

    while not connected:
        connectivity_graph = nx.erdos_renyi_graph(n=Settings.NUM_AGENTS, p=Settings.CONNECTIVITY_GRAPH_EDGE_PROPORTION)
        connected = nx.is_connected(connectivity_graph)

    nx.draw(connectivity_graph)
    plt.show()

    return connectivity_graph


def generate_matching_graph():
    matching_graph = nx.complete_bipartite_graph(Settings.NUM_LEFT, Settings.NUM_RIGHT)
    for _, _, d in matching_graph.edges(data=True):
        d['weight'] = random.randint(*Settings.MATCHING_WEIGHTS_LIMITS)

    global do_once_full_graph
    if do_once_full_graph:
        draw_bipartite_graph(matching_graph)
        do_once_full_graph = False

    return matching_graph


def draw_bipartite_graph(matching_graph):
    l, r = nx.bipartite.sets(matching_graph)
    pos = {}
    # Update position for node from each group
    pos.update((node, (1, index)) for index, node in enumerate(l))
    pos.update((node, (2, index)) for index, node in enumerate(r))
    nx.draw(matching_graph, pos=pos)
    plt.show()


def is_solved(agents: List[AgentBase], matching_graph: nx.Graph) -> bool:
    solutions = [agent.get_solution() for agent in agents]

    if not is_valid_matching(matching_graph=matching_graph, solutions=solutions):
        return False

    # Calculate discrepancy
    average_discrepancy = calculate_average_discrepancy(agents)

    # calculate matching score ,
    matching_score = calc_matching_score(agents=agents, matching_graph=matching_graph)
    optimal_matching_weight = calc_optimal_matching_weight(matching_graph)

    return (average_discrepancy <= Settings.DISCREPANCY_THRESHOLD and
            matching_score >= optimal_matching_weight * Settings.MIN_ALLOWED_MATCHING_SCORE_PROPORTION)


def calc_optimal_matching_weight(matching_graph) -> int:
    optimal_matching = nx.algorithms.matching.max_weight_matching(matching_graph)
    optimal_matching_weight = 0
    for edge in optimal_matching:
        optimal_matching_weight += matching_graph.get_edge_data(*edge)['weight']

    return optimal_matching_weight


def is_valid_matching(matching_graph: nx.Graph, solutions: List[MatchingSolution]) -> bool:
    for solution in solutions:
        if solution is None or not nx.is_matching(matching_graph, set(solution)):
            return False

    return True
