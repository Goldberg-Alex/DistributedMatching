from typing import List, Dict

import networkx as nx

import Settings
from AgentBase import AgentBase, Message, AgentID, MatchingSolution


class Agent(AgentBase):
    def __init__(self,
                 agent_idx: int,
                 matching_subgraph: nx.Graph,
                 connectivity_graph: nx.Graph):
        super().__init__(agent_idx, matching_subgraph, connectivity_graph)
        self._is_done = False
        self._matching = None

        self._received_new_data = True

    def step(self, message_budget, messages: List[Message]) -> Dict[AgentID, Message]:
        count_before = self._count_weighted_edges(self._matching_subgraph)

        for message in messages:
            self._matching_subgraph = self.append_subgraph(self._matching_subgraph, message.data)
        count_after = self._count_weighted_edges(self._matching_subgraph)
        # print(f"num messages: {len(messages)}")
        # print(f"count before = {count_before}, count after = {count_after}")
        out_messages = {}
        if self._received_new_data:
            out_messages = {agent_idx: Message(self._matching_subgraph) for agent_idx in range(Settings.NUM_AGENTS) if
                            self._connectivity_graph.has_edge(agent_idx, self._agent_idx)}
            self._received_new_data = False
        return out_messages

    def is_done(self) -> bool:
        if self._count_weighted_edges(self._matching_subgraph) < len(self._matching_subgraph.edges):
            # print(f"weighted edges = {self._count_weighted_edges(self._matching_subgraph)}/"
            #       f" {len(self._matching_subgraph.edges)}")
            return False

        self._matching = nx.algorithms.matching.max_weight_matching(self._matching_subgraph)
        return True

    def get_solution(self) -> MatchingSolution:
        return self._matching

    def append_subgraph(self, original_subgraph: nx.Graph, additional_subgraph: nx.Graph) -> nx.Graph:
        for edge in additional_subgraph.edges(data=True):
            if edge[2]['weight'] > 0:
                original_subgraph.get_edge_data(*edge)['weight'] = edge[2]['weight']
                self._received_new_data = True
        return original_subgraph
