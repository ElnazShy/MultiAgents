# Types for agents are 'L1','L2','F1','F2'
import agent
import position
import a_star
import MCTS

dx = [1, 0, -1, 0]  # 0: left,  1:up, 2:right  3:down
dy = [0, 1, 0, -1]


class simulator:
    def __init__(self,the_map ,items ,agents,n,m):
        self.the_map = the_map
        self.items = items
        self.agents = agents
        self.memory = position.position(0, 0)
        self.n = n
        self.m = m


    def get_first_action(self,route):
        #print '~~~~~~~~~~~~~~~~~~~~~~~  route : ' , route
        dir = route[0]
        #print 'dir: ' + dir
        if dir == '0':
            return 'W'
        if dir == '1':
            return 'N'
        if dir == '2':
            return 'E'
        if dir == '3':
            return 'S'

    def items_left(self):
        items_count= 0
        for i in range (0,len(self.items)):
            if not self.items[i].loaded:
                items_count += 1
        return items_count

    def update_map(self,old_pos,new_pos):
        print(old_pos,new_pos)
        print("8888888888888888888888888888888888888888888888888888")
        self.draw_map()
        (x,y) =  old_pos
       # print old_pos
        self.the_map[y][x]= 0
        agent_index = self.find_agent_index(old_pos)
        self.agents[agent_index].pos = new_pos
        (x, y) = new_pos
        #print 'the_map[y][x] = 8 ', new_pos

        self.the_map[y][x] = 8  # 8 demonstrate the unknown agent on the map
        print("8888888888888888888888888888888888888888888888888888")
        self.draw_map()
        return

    def find_agent_index (self,pos):
        agents_num = len(self.agents)
        for i in range (0, agents_num):

            if self.agents[i].pos == pos :
                return i
        return -1

    def remove_old_destination_in_map(self):

        for y in range(self.m):
            for x in range(self.n):
                xy = self.the_map[y][x]
                if xy == 4:
                    self.the_map[y][x] = 1

    def mark_route_map(self,route,xA,yA,dx,dy):
        x = xA
        y = yA

        if len(route) > 0:
            for i in range(len(route)):
                j = int(route[i])
                x += dx[j]
                y += dy[j]
                self.the_map[y][x] = 3


    def draw_map(self):

        for y in range(self.m):
            for x in range(self.n):
                xy = self.the_map[y][x]
                if xy == 0:
                    print('.')  # space
                elif xy == 1:
                    print('I')  # Items
                #elif xy == 2:
                #    print 'S',  # start
                #elif xy == 3:
                 #   print 'R',  # route
                #elif xy == 4:
                 #   print 'F',  # finish
                elif xy == 8:
                    print('A')  # Unnown Agent
                elif xy == 9:
                    print('M')  # Main Agent
            print

    def set_map(self, the_map):
        self.the_map = the_map

    def agent_next_item(self, agent_position, item_position):

        (xA, yA) = agent_position
        (xI, yI) = item_position
        if (yI == yA and abs(xA - xI) == 1) or (xI == xA and abs(yA - yI) == 1):
            return True
        else:
            return False

    def load_item(self, agent, item_index):

        (xA, yA) = agent.get_position()
        (xI, yI) = self.items[item_index].get_position()
        self.items[item_index].loaded = True

        dx = xI - xA
        dy = yI - yA

        self.the_map[yA][xA] = 0
        self.the_map[yI][xI] = 8

        return (dx, dy)


################################################################################################################
    def run_and_update(self, agent):

        #print '**** running simulator'
        dx = [1, 0, -1, 0]  # 0:E ,  1:N , 2:w  3:S
        dy = [0, 1, 0, -1]

        unknown_agent = agent

        location = unknown_agent.position  # Location of main agent
        destination = position.position(0, 0)

        # If the target is selected before we have it in memory variable and we can use it
        if self.memory.get_position() != (0, 0) and location != self.memory:
            destination = self.memory

        else:  # If there is no target we should choose a target based on visible items and agents.
            unknown_agent.visible_agents_items(self.items,self.agents)
            target = unknown_agent.choose_target(self.items,self.agents)

            if target.get_position() != (0, 0):
                destination = target
            else:
                return unknown_agent

            self.memory = destination

        if destination.get_position() == (0, 0):

            unknown_agent.set_actions_probability(0, 0.25, 0.25, 0.25, 0.25)
            return unknown_agent

        else:

            (xA, yA) = unknown_agent.get_position() # Get start position

            self.remove_old_destination_in_map()

            (xB, yB) = destination.get_position() # Get the target position
            #self.the_map[yB][xB] = 4 # Update map with targer position

            # If agent is next to the target item, it should load it.
            item_index = unknown_agent.is_item_nearby(self.items)

            if item_index != -1:
                print('****** load')

                # load item and remove it from map and get the direction to reach the item.
                (dx,dy) = self.load_item(unknown_agent,item_index)

                unknown_agent.next_action = 'L'
                loaded_item_position = self.items[item_index].get_position()

                # Set the position of agent with the position of the target item. As agent reach it and load it.
                unknown_agent.set_position(loaded_item_position[0],loaded_item_position[1])
                new_position = loaded_item_position
                unknown_agent.change_direction(dx,dy)
                self.agents[unknown_agent.index] = unknown_agent

                # Empty the memmory to choose new target
                self.memory = position.position(0, 0)

            else:

                a = a_star.a_star(self.the_map, dx, dy)

                route = a.pathFind(xA, yA, xB, yB)

                self.mark_route_map(route,xA, yA,dx,dy)

                #self.draw_map()

                if len(route) == 0:
                    return unknown_agent

                action = self.get_first_action(route)

                unknown_agent.next_action = action
                unknown_agent.set_probability_main_action()
                new_position = unknown_agent.change_position_direction(self.n,self.m)
                unknown_agent.set_position(new_position[0], new_position[1])
                self.agents[unknown_agent.index] = unknown_agent

            self.update_map((xA, yA), new_position)

            return unknown_agent

################################################################################################################
    def mcts_move(self,parameters_estimation):
        self = MCTS.move_agent(self, parameters_estimation)
        return

    def run(self, agent):

        # print '**** running simulator'
        dx = [1, 0, -1, 0]  # 0:E ,  1:N , 2:w  3:S
        dy = [0, 1, 0, -1]

        unknown_agent = agent

        location = unknown_agent.position  # Location of main agent
        destination = position.position(0, 0)

        # If the target is selected before we have it in memory variable and we can use it
        if self.memory.get_position() != (0, 0) and location != self.memory:
            destination = self.memory

        else:  # If there is no target we should choose a target based on visible items and agents.
            unknown_agent.visible_agents_items(self.items, self.agents)
            target = unknown_agent.choose_target(self.items, self.agents)

            if target.get_position() != (0, 0):
                destination = target
            else:
                return unknown_agent

            self.memory = destination

        if destination.get_position() == (0, 0):

            unknown_agent.set_actions_probability(0, 0.25, 0.25, 0.25, 0.25)
            return unknown_agent

        else:

            (xA, yA) = unknown_agent.get_position()  # Get start position

            self.remove_old_destination_in_map()

            (xB, yB) = destination.get_position()  # Get the target position
            self.the_map[yB][xB] = 4  # Update map with targer position

            # If agent is next to the target item, it should load it.
            if self.agent_next_item((xA, yA), (xB, yB)):
                print('****** load')

                # load item and remove it from map and get the direction to reach the item.

                unknown_agent.next_action = 'L'

                # Empty the memmory to choose new target
                self.memory = position.position(0, 0)

            else:

                a = a_star.a_star(self.the_map, dx, dy)

                route = a.pathFind(xA, yA, xB, yB)

                if len(route) == 0:
                    return unknown_agent

                action = self.get_first_action(route)
                #  print 'action: ' , action
                unknown_agent.next_action = action
                unknown_agent.set_probability_main_action()

            return unknown_agent

