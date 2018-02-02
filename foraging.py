import agent
import item
import random
import simulator


items = []
agents = []
the_map = []


def initialize_items_agents_notrandom(n,m):
    # generating choices for random selection
    global the_map

    sf=[]
    sf.append((1, 2))
    sf.append((1, 5))
    sf.append((3, 4))
    sf.append((5, 8))
    sf.append((8, 1))
    sf.append((6, 2))
    sf.append((5, 4))
    sf.append((9, 4))
    sf.append((2, 6))
    sf.append((9, 9))

    # creating items
    for i in range(0, 10):
        (x, y) = sf[i]
        tmp_item = item.item(x, y, 1)
        items.append(tmp_item)
        the_map[y][x] = 1

    # creating agent
    (x, y) = (4,4)
    unknown_agent = agent.Agent(x, y,'l1')
    the_map[y][x] = 8
    agents.append(unknown_agent)


    (x, y) = (1,1)
    main_agent = agent.Agent(x, y,'l1')
    agents.append(main_agent)
    the_map[y][x] = 9


def initialize_items_agents(n,m):
    # generating choices for random selection
    global the_map
    sf = []
    for i in range(0, n):
        for j in range(0, m):
            sf.append((i, j))


    # creating items
    for i in range(1, 10):
        (x, y) = random.choice(sf)
        tmp_item = item.item(x, y, 1)
        items.append(tmp_item)
        sf.remove((x, y))
        the_map[y][x] = 1

    # creating agent
    (x, y) = random.choice(sf)
    unknown_agent = agent.Agent(x, y,'l1')
    the_map[y][x] = 8
    agents.append(unknown_agent)
    sf.remove((x, y))

    (x, y) = random.choice(sf)
    main_agent = agent.Agent(x, y,'l1')
    agents.append(main_agent)
    sf.remove((x, y))
    the_map[y][x] = 9


def create_empty_map(n,m):
    #create the map

    row = [0] * n

    for i in range(m):
        the_map.append(list(row))


n = 10  # horizontal size,column
m = 10  # vertical size ,row

create_empty_map(n,m)
#initialize_items_agents(n, m)
initialize_items_agents_notrandom(n,m)


sim = simulator.simulator(the_map, items, agents,n,m)

for y in range(m):
    for x in range(n):
        xy = the_map[y][x]
        if xy == 0:
            print('.')  # space
        elif xy == 1:
            print('I')  # Items
        elif xy == 2:
            print('S')  # start
        elif xy == 3:
            print('R')  # route
        elif xy == 4:
            print('F')  # finish
        elif xy == 8:
            print('A')  # Unknown Agent
        elif xy == 9:
            print('M')  # Main Agent
    print

true_radius = 0.48
true_angle = 0.42
true_level = 0.76

unknown_agent = agents[0]
unknown_agent.set_parameters(true_level, true_radius, true_angle, n, m)

map_history = list()
map_history.append(the_map)

for t in range(0, 8):
    unknown_agent = sim.run(unknown_agent)
    #print unknown_agent.direction


