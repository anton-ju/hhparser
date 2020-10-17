siblings = ['p2', 'p3', 'p1']

stacks = {'p1': 1012, 'p2': 484, 'p3': 464, 'p4': 40, 'p5': 464, 'p6': 494}

name = 'p4'

# how many elements left in list after index 'name'
knocks = sum([stacks[name] >= stacks[s] for s in siblings])
print(knocks)


