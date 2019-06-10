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
    # [mainpot, side1pot, side2pot]
    pots = [182, 1272, 40]
    # uncalled for top1 player
    uncalled = 548
    root = Node('root')
    add_children(root, aiplayers)
    paths = []
    for pre, fill, node in RenderTree(root):
        if node.is_leaf:
            path = []
            for p in node.path:
                path.append(p.name)
            paths.append((path[1:]))
    print(paths)

    outcomes = []
    for path in paths:
        pots_ = pots[:]

        stack = {}
        for player in reversed(path):
            stack[player] = pots_.pop()

        # all the rest pots to first player in path
        stack[path[0]] += sum(pots_)
        # stacks for players that is not take part in pots remains the same
        for p in not_aiplayers:
            stack[p] = stacks[p]
        outcomes.append(stack)

        # players who lose.
        for p in aiplayers:
            if p not in path:
                stack[p] = 0

        # uncalled allways to top1 player
        try:
            stack[aiplayers[0]] += uncalled
        except KeyError:
            stack[aiplayers[0]] = uncalled

    printer = pp()
    printer.pprint(outcomes)


build_outcome_tree()
