from anytree import Node, NodeMixin, RenderTree
from pprint import PrettyPrinter as pp

def add_children(root, children):
    if len(children) <= 1:
        return
    for i in range(len(children)):
        new_root = Node(children[i], parent=root)
        add_children(new_root, children[:i])


def build_outcome_tree():
    aiplayers = ['p1', 'p2', 'p3', 'p4']

    stacks = {'p1': 1012, 'p2': 484, 'p3': 464, 'p4': 40, 'p5': 464, 'p6': 494}
    not_aiplayers = [p for p in stacks.keys() if p not in aiplayers]
    # [side2pot, side1pot, mainpot]
    pots = [40, 1272, 182]
    # [players_in_pot[0] - corresponds to list of players in side2 pot
    # [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
    players_in_pot = [aiplayers[:l] for l in range(len(pots)+1, 1, -1)]
    # uncalled for top1 player
    uncalled = 548
    root = Node('root')
    add_children(root, aiplayers)
    paths = []
    # creating all paths list if node is leaf
    for pre, fill, node in RenderTree(root):
        # leaf of the tree representing 1 outcome
        if node.is_leaf:
            path = []
            for p in node.path:
                # path looks like (node, siblings of node)
                path.append((p.name, len(p.siblings) - 1))
            # not including first path element, because its alwayes root
            paths.append((path[1:]))
    print(paths)

    outcomes = []
    # building outcomes from path list
    for path in paths:
        pots_ = pots[:]

        players_in_path = []
        stack = {}
        for player, pot_index in path:
            stack[player] = sum([potsots_.pop(pot_index)
            players_in_path.append(player)

        # all the rest pots to first player in path
        stack[path[0][0]] += sum(pots_)
        # stacks for players that is not take part in pots remains the same
        for p in not_aiplayers:
            stack[p] = stacks[p]

        # players who lose.
        for p in aiplayers:
            if p not in players_in_path:
                stack[p] = 0

        # uncalled allways to top1 player
        try:
            stack[aiplayers[0]] += uncalled
        except KeyError:
            stack[aiplayers[0]] = uncalled
        outcomes.append(stack)

    printer = pp()
    printer.pprint(outcomes)


build_outcome_tree()
