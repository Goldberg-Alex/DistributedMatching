from typing import Any, List, Tuple, Dict, Set

import networkx as nx

# the last element of an edge is a dictionary of {'weight': w} where w is the weight of the edge
Edge = Tuple[int, int]
MatchingSolution = Set[Edge]
AgentID = int


class Message:
    def __init__(self, data: Any):
        self.data = data


class AgentBase:
    def __init__(self,
                 agent_idx: int,
                 matching_subgraph: nx.Graph,
                 connectivity_graph: nx.Graph):
        self._agent_idx = agent_idx
        self._matching_subgraph = matching_subgraph
        self._connectivity_graph = connectivity_graph

    @property
    def agent_idx(self) -> AgentID:
        return self._agent_idx

    def step(self, message_budget, messages: List[Message]) -> Dict[AgentID, Message]:
        pass

    def is_done(self) -> bool:
        return False

    def get_solution(self) -> MatchingSolution:
        pass

    def __eq__(self, other):
        return isinstance(other, AgentBase) and self.agent_idx == other.agent_idx

    def _count_weighted_edges(self, graph):
        count = 0

        for edge in graph.edges(data=True):
            count += (edge[2]['weight'] > 0)

        return count
