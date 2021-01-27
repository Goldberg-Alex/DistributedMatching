import concurrent.futures
from typing import Dict, List, Tuple

import networkx as nx

import Settings
from AgentBase import AgentID, Message
from NormalAgent import Agent
from Utilities import generate_matching_graph, generate_matching_sub_graphs, generate_connectivity_graph, \
    is_solved

'''
how to use this file:
run it.!
'''


def main(message_budget) -> Tuple[bool, int]:
    # generate matching graph with random weights
    matching_graph = generate_matching_graph()

    sub_graphs = generate_matching_sub_graphs(matching_graph)
    connectivity_graph = generate_connectivity_graph()
    agents = generate_agents(connectivity_graph, sub_graphs)

    budget_used = 0
    curr_message_budget = message_budget
    prev_round_messages: Dict[AgentID, List[Message]] = {}
    agents_done = False

    # run untill all agents are done or the message budget is 0
    while curr_message_budget > 0 and not agents_done:
        curr_round_messages: Dict[AgentID, List[Message]] = {}
        agents_done = True

        # iterate over agents, pass them the current messages and get the messages for the next round
        for agent in agents:
            # run an agent step
            new_messages = agent.step(message_budget=curr_message_budget,
                                      messages=prev_round_messages.get(agent.agent_idx, []))
            # check if the agent is done.
            # The rounds stop only if all agents are done
            agents_done = agents_done and agent.is_done()

            # save the agent's messages for the next round
            for recipient_idx, message in new_messages.items():
                # messages that are addressed to an agent which is not a neighbor are discarded
                if not connectivity_graph.has_edge(agent.agent_idx, recipient_idx):
                    continue

                if curr_message_budget <= 0:
                    break

                if recipient_idx not in curr_round_messages.keys():
                    curr_round_messages[recipient_idx] = []
                # add the message to the next round's messages
                curr_round_messages[recipient_idx].append(message)

                # each message decreases the budget by 1
                curr_message_budget -= 1
                budget_used += 1

        prev_round_messages = curr_round_messages

    # last iteration to pass the last message
    for agent in agents:
        agent.step(message_budget=curr_message_budget,
                   messages=prev_round_messages.get(agent.agent_idx, []))

    return (is_solved(agents=agents, matching_graph=matching_graph), budget_used)


def generate_agents(connectivity_graph: nx.Graph, sub_graphs: List[nx.Graph]) -> List[Agent]:
    agents = []
    for agent_idx in range(Settings.NUM_AGENTS):
        agents.append(Agent(agent_idx=agent_idx,
                            matching_subgraph=sub_graphs.pop(),
                            connectivity_graph=connectivity_graph))
    return agents


if __name__ == '__main__':
    """This is the main function for the golfing challenge"""
    budgets_used = []
    solved_list = []
    # we can swap out ProcessPoolExecutor for ThreadPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for solved, budget in executor.map(main, [Settings.EASY_DIFFICULTY]*Settings.NUM_RUNS):
            # put results into correct output list
            solved_list.append(solved)
            budgets_used.append(budget)

    if False in solved_list:
        print("failed to solve, exiting")
        exit()

        budgets_used.append(budget)

    budgets_used.sort()
    average_budget_used = sum(budgets_used[0:int(Settings.CONSIDERED_RESULTS)]) / Settings.CONSIDERED_RESULTS

    relative_budget = round(average_budget_used / Settings.NUM_AGENTS, 4)
    print(f"Budget used: {relative_budget} * n ")
