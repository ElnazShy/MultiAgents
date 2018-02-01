from math import *
import random
import simulator
import item
import agent

map = []

class State:

    def __init__(self, sim):
        self.the_map = sim.the_map  # At the root pretend the player just moved is p2 - p1 has the first move
        self.sim = sim
        self.items = sim.items
        self.agents = sim.agents
        self.sim.agents[1].reward = 0
        self.options = ['N', 'S', 'E', 'W']

    def Clone(self):
        state = State(self.sim)
        return state

    def DoMove(self, move, mode):

        (xM, yM) = self.sim.agents[1].get_position()

        self.sim.agents[1].next_action = move
        (xA, yA) = self.sim.agents[1].change_position_direction(10, 10)
        get_reward = False
        self.sim.agents[1].position = (xA, yA)
        print (xA, yA)
        if self.sim.the_map[yA][xA] == 1:  # load item
            nearby_item_index = self.sim.get_item_by_position(xA, yA)
            self.sim.load_item(self.sim.agents[1],nearby_item_index)
            self.sim.agents[1].reward += 1
            get_reward = True
            (xA, yA) = self.sim.items[nearby_item_index].get_position()
        # else: # Move
        self.sim.update_map_mcts((xM, yM), (xA, yA))
        return get_reward

    def GetMoves(self):
        return self.options

    def GetResult(self):
        return self.sim.agents[1].reward


class Node:

    def __init__(self, move=None, parent=None, state=None):
        self.move = move  # the move that got us to this node - "None" for the root node
        self.parentNode = parent  # "None" for the root node
        self.childNodes = []
        self.rewards = 0
        self.visits = 0
        self.untriedMoves = ['N', 'S', 'E', 'W']

    def UCTSelectChild(self):

        s = sorted(self.childNodes, key=lambda c: c.rewards / c.visits + sqrt(2 * log(self.visits) / c.visits))[-1]
        return s

    def AddChild(self, m, s):

        n = Node(move=m, parent=self, state=s)
        self.untriedMoves.remove(m)
        self.childNodes.append(n)

        return n

    def Update(self, result):

        self.visits += 1
        self.rewards += result


def UCT(local_sim, itermax, parameters_estimation):

    rootnode = Node()
    node = rootnode

    for i in range(itermax):
        node = rootnode
        tmp_state = State(local_sim)

        # Select
        # node.untriedMoves == [] ??

        while node.untriedMoves == [] and node.childNodes != []:
            # node is fully expanded and non-terminal
            # if we try all possible moves and current node has a child then select a node to expand
            # We will move till reaching a leaf which don't have any child and we don't

            node = node.UCTSelectChild()
            tmp_state.DoMove(node.move,'S')

        # Expand
        if node.untriedMoves != []:  # if we can expand (i.e. state/node is non-terminal)
            m = random.choice(node.untriedMoves)
            tmp_state.DoMove(m,'S')
            node = node.AddChild(m, tmp_state)  # add child and descend tree

        # Rollout - this can often be made orders of magnitude quicker using a state.GetRandomMove() function
        rollout_max = 10
        rollout_count = 0
        node_reward = 0
        while rollout_count < rollout_max:  # while state is non-terminal
            move = random.choice(tmp_state.GetMoves())
            get_reward = tmp_state.DoMove(move,'S')
            if get_reward:
                node_reward += 1

            rollout_count += 1
            tmp_state.agents[0].set_parameters(parameters_estimation[0], parameters_estimation[1], parameters_estimation[2])
            tmp_state.sim.run_and_update(tmp_state.agents[0])

        # # print "********** UCT Backpropagate ", i
        # Backpropagate
        # print("reward" , node_reward)
        while node != None:  # backpropagate from the expanded node and work back to the root node
            node.Update(node_reward)
            node = node.parentNode

    return sorted(rootnode.childNodes, key=lambda c: c.visits)[-1].move  # return the move that was most visited


def move_agent(agents, items, parameters):

    local_map = []
    row = [0] * 10

    for i in range(10):
        local_map.append(list(row))

    local_items = []
    for i in range(len(items)):
        (item_x,item_y) = items[i].get_position()
        local_item = item.item(item_x, item_y, 1, i)
        local_items.append(local_item)
        local_map[item_y][item_x] = 1

    local_agents = list()

    (a_agent_x,a_agent_y) = agents[0].get_position()
    local_map[a_agent_y][a_agent_x] = 8
    local_agent = agent.Agent(a_agent_x, a_agent_y, 'l1', 0)
    local_agents.append(local_agent)

    (m_agent_x, m_agent_y) = agents[1].get_position()
    local_map[m_agent_y][m_agent_x] = 9
    local_agent = agent.Agent(m_agent_x, m_agent_y, 'l1', 1)
    local_agents.append(local_agent)



    real_sim = simulator.simulator(local_map, local_items, local_agents,10, 10 )
    next_move = UCT(real_sim, itermax=2, parameters_estimation = parameters)
    print "^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^" ,next_move
    return next_move

