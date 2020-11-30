from typing import List, Dict

from AgentBase import AgentBase, Message, AgentID, MatchingSolution
import networkx as nx


class Agent(AgentBase):
    def __init__(self,
                 agent_idx: int,
                 matching_subgraph: nx.Graph,
                 connectivity_graph: nx.Graph):
        super().__init__(agent_idx, matching_subgraph, connectivity_graph)

    def step(self, message_budget, messages: List[Message]) -> Dict[AgentID, Message]:
        return {self.agent_idx: Message(None)}

    def is_done(self) -> bool:
        return True

    def get_solution(self) -> MatchingSolution:
        matching = nx.algorithms.matching.max_weight_matching(self.full_matching_graph)
        return matching

    def set_graph(self, graph):
        self.full_matching_graph = graph
