aiplayers = ['p1', 'p2', 'p3', 'p4']

stacks = {'p1': 1012, 'p2': 484, 'p3': 464, 'p4': 40, 'p5': 464, 'p6': 494}
not_aiplayers = [p for p in stacks.keys() if p not in aiplayers]
# [side2pot, side1pot, mainpot]
pots = [40, 1272, 182]
# [players_in_pot[0] - corresponds to list of players in side2 pot
# [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
players_in_pot = list(reversed([aiplayers[:l] for l in range(len(pots)+1, 1, -1)]))
print(players_in_pot)

path1 = ['p2', 'p3', 'p4']
path2 = ['p1', 'p4']
path3 = ['p2', 'p3']

outcomes = []
for path in [path1, path2, path3]:
    stack = {}
    p_index = 0
    for i, pot in enumerate(pots):
        #import pdb; pdb.set_trace()
        print(f'i: {i}, p_index: {p_index}, path: {path}, pot: {pot}, players_in_pot: {players_in_pot[i]}')
        if path[p_index] in players_in_pot[i]:
            try:
                stack[path[p_index]] += pots[i]
            except KeyError:
                stack[path[p_index]] = pots[i]
            p_index = p_index + 1 if p_index < len(path) - 1 else p_index
        else:
            stack[path[p_index-1]] = stack[path[p_index-1]] + pots[i]
    outcomes.append(stack)
print(outcomes)
