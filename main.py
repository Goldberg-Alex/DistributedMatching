from typing import Dict, List

import networkx as nx

import Settings
from AgentBase import Message, AgentID, AgentBase
from SmartAgent import Agent
from Utilities import generate_matching_graph, generate_matching_sub_graphs, generate_connectivity_graph, \
    is_solved


def main(message_budget) -> bool:
    # generate matching graph with random weights
    # random.seed(1)

    matching_graph = generate_matching_graph()

    sub_graphs = generate_matching_sub_graphs(matching_graph)
    connectivity_graph = generate_connectivity_graph()
    agents = generate_agents(connectivity_graph, sub_graphs)

    curr_message_budget = message_budget
    prev_round_messages: Dict[AgentID, List[Message]] = {}
    agents_done = False

    while curr_message_budget > 0 and not agents_done:
        curr_round_messages: Dict[AgentID, List[Message]] = {}
        agents_done = True

        for agent in agents:

            new_messages = agent.step(message_budget=curr_message_budget,
                                      messages=prev_round_messages.get(agent.agent_idx, []))
            agents_done = agents_done and agent.is_done()

            for recipient_idx, message in new_messages.items():
                if not connectivity_graph.has_edge(agent.agent_idx, recipient_idx):
                    print(f"Message sent from: agent {agent.agent_idx} to an invalid recipient: agent {recipient_idx}. "
                          f"Ignoring message.")
                    continue

                if curr_message_budget <= 0:
                    break
                if recipient_idx not in curr_round_messages.keys():
                    curr_round_messages[recipient_idx] = []

                curr_round_messages[recipient_idx].append(message)
                curr_message_budget -= 1

        prev_round_messages = curr_round_messages

    # last iteration to pass the last message
    for agent in agents:
        agent.step(message_budget=curr_message_budget,
                   messages=prev_round_messages.get(agent.agent_idx, []))

    if is_solved(agents=agents, matching_graph=matching_graph):
        print(f"solved, used messages: {message_budget - curr_message_budget} / {message_budget}.")
        return True

    return False


def generate_agents(connectivity_graph: nx.Graph, sub_graphs: List[nx.Graph]) -> List[AgentBase]:
    agents = []
    for agent_idx in range(Settings.NUM_AGENTS):
        agents.append(Agent(agent_idx=agent_idx,
                            matching_subgraph=sub_graphs.pop(),
                            connectivity_graph=connectivity_graph))
    return agents


if __name__ == '__main__':
    if main(Settings.NUM_AGENTS ** 3):
        print("**************EASY test - passed")

        if main(Settings.NUM_AGENTS ** 2):
            print("**************MEDIUM test - passed")

            if main(Settings.NUM_AGENTS):
                print("**************HARD test - passed! ")
                print("Congratulations, you passed the tutorial.")
                print("Now, prove P != NP")
            else:
                print("**************HARD test - failed")
        else:
            print("**************MEDIUM test - failed")
    else:
        print("**************EASY test - failed")
