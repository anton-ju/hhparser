from anytree import NodeMixin, RenderTree
from pprint import PrettyPrinter as pp


class OutCome(NodeMixin, object):

    def __init__(self, name, parent=None, children=None, chips={}, probs={}, knocks={}, **kwargs):
        self.__dict__.update(kwargs)
        self.name = name
        self.chips = chips
        self.probs = probs
        self.knocks = knocks
        self.parent = parent
        if children:
            self.children = children

    def __repr__(self):
        args = ["%r" % self.separator.join([""] + [str(node.name) for node in self.path])]
        return _repr(self, args=args, nameblacklist=["name"])


def add_children(root, children):
    if len(children) <= 1:
        return
    for i in range(len(children)):
        new_root = OutCome(children[i], parent=root, )
        add_children(new_root, children[:i])


def build_outcome_tree():
    aiplayers = ['p1', 'p2', 'p3', 'p4']

    stacks = {'p1': 1012, 'p2': 484, 'p3': 464, 'p4': 40, 'p5': 464, 'p6': 494}
    not_aiplayers = [p for p in stacks.keys() if p not in aiplayers]
    # [side2pot, side1pot, mainpot]
    pots = [40, 1272, 182]
    # [players_in_pot[0] - corresponds to list of players in side2 pot
    # [players_in_pot[1] - corresponds to list of players in side1 pot and so on 
    players_in_pot = list(reversed([aiplayers[:l] for l in range(len(pots)+1, 1, -1)]))
    # uncalled for top1 player
    uncalled = 548
    root = OutCome('root')
    add_children(root, aiplayers)
    paths = []
    # creating all paths list if node is leaf
    for pre, fill, node in RenderTree(root):
        # leaf of the tree representing 1 outcome
        if node.is_leaf:
            path = []
            for p in node.path:
                # path looks like [node.name, node.name...]
                path.append(p.name)
            # not including first path element, because its alwayes root
            path = list(reversed(path[1:]))

            stack = {}
            p_index = 0
            for i, pot in enumerate(pots):
                #print(f'i: {i}, p_index: {p_index}, path: {path}, pot: {pot}, players_in_pot: {players_in_pot[i]}')
                if path[p_index] in players_in_pot[i]:
                    try:
                        stack[path[p_index]] += pots[i]
                    except KeyError:
                        stack[path[p_index]] = pots[i]
                    p_index = p_index + 1 if p_index < len(path) - 1 else p_index
                else:
                    stack[path[p_index-1]] = stack[path[p_index-1]] + pots[i]

            # stacks for players that is not take part in pots remains the same
            for p in not_aiplayers:
                stack[p] = stacks[p]

            # players who lose.
            for p in aiplayers:
                if p not in path:
                    stack[p] = 0

            # uncalled allways to top1 player
            try:
                stack[aiplayers[0]] += uncalled
            except KeyError:
                stack[aiplayers[0]] = uncalled

            node.chips = stack
            #print(node.chips)
            knocks = {}
            for n in node.path:
                knocks_sum = sum([stacks[n.name] >= stacks[s.name] for s in n.siblings])
                if knocks_sum:
                    knocks[n.name] = knocks_sum
            node.knocks = knocks
    return root


root = build_outcome_tree()
stacks = {'p1': 1012, 'p2': 484, 'p3': 464, 'p4': 40, 'p5': 464, 'p6': 494}
print(stacks)
for pre, _, node in RenderTree(root):
    print("%s %s %s %s" % (pre, node.name, node.chips, node.knocks))
