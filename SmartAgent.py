import dataclasses as dc
import random
from typing import List, Dict

import networkx as nx
import numpy as np

import Settings
from AgentBase import AgentBase, Message, AgentID, MatchingSolution
from Utilities import generate_matching_graph, generate_matching_sub_graphs, calc_optimal_matching_weight


@dc.dataclass
class AgentMessage:
    pass


def calc_matching_expected_value():
    matching_scores = []
    for _ in range(2):
        matching_graph = generate_matching_graph()
        sub_graphs = generate_matching_sub_graphs(matching_graph)
        for graph in sub_graphs:
            matching_scores.append(calc_optimal_matching_weight(graph))

    return np.mean(matching_scores), np.var(matching_scores)


class Agent(AgentBase):
    matching_mean, matching_variance = calc_matching_expected_value()

    def __init__(self,
                 agent_idx: int,
                 matching_subgraph: nx.Graph,
                 connectivity_graph: nx.Graph):

        super().__init__(agent_idx, matching_subgraph, connectivity_graph)
        self._is_done = False
        self._matching = None
        self.step_num = 0
        self._received_new_data = True
        self._calc_possible_recipients()

    def step(self, message_budget, messages: List[Message]) -> Dict[AgentID, Message]:
        self.step_num += 1

        self._merge_messages(messages)

        out_messages = {}

        if self._is_good_enough_for_sending(message_budget):
            out_messages = {agent_idx: Message(self._matching_subgraph) for agent_idx in self._calc_recipients()}
            self._received_new_data = False
        return out_messages

    def is_done(self) -> bool:
        if self._count_weighted_edges(self._matching_subgraph) < len(self._matching_subgraph.edges):
            # print(f"weighted edges = {self._count_weighted_edges(self._matching_subgraph)}/"
            #       f" {len(self._matching_subgraph.edges)}")
            return False

        self._matching = nx.algorithms.matching.max_weight_matching(self._matching_subgraph)
        return True

    def _is_good_enough_for_sending(self, message_budget) -> bool:
        current_matching = calc_optimal_matching_weight(self._matching_subgraph)
        sending_threshold = self.matching_mean + self.matching_variance * 2 - message_budget - self.step_num

        return current_matching > sending_threshold

    def _calc_possible_recipients(self):
        self.possible_recipients = [agent_idx for agent_idx in range(Settings.NUM_AGENTS)
                                    if self._connectivity_graph.has_edge(agent_idx, self._agent_idx)]

    def _calc_recipients(self) -> List[AgentID]:
        random.shuffle(self.possible_recipients)
        return [self.possible_recipients[0]]

    def _merge_messages(self, messages):
        self._received_new_data = False
        count_before = self._count_weighted_edges(self._matching_subgraph)
        for message in messages:
            self._matching_subgraph = self._append_subgraph(self._matching_subgraph, message.data)
            self._received_new_data = True

        count_after = self._count_weighted_edges(self._matching_subgraph)
        if count_after != count_before:
            print(f"num messages: {len(messages)}")
            print(f"count before = {count_before}, count after = {count_after}")

    def get_solution(self) -> MatchingSolution:
        return self._matching

    def _append_subgraph(self, original_subgraph: nx.Graph, additional_subgraph: nx.Graph) -> nx.Graph:
        for edge in additional_subgraph.edges(data=True):
            if edge[2]['weight'] > 0:
                original_subgraph.get_edge_data(*edge)['weight'] = edge[2]['weight']
                self._received_new_data = True
        return original_subgraph
