from pyevidence import *
from itertools import product


people  = ["plum", "scarlett", "mustard", "white", "green", "peacock"]

places  = ["kitchen", "ballroom", "conservatory", "dining room",
          "billiard room", "library", "lounge", "hall", "study"]

weapons = ["candlestick", "dagger", "lead-pipe", "revolver", "rope",
           "spanner"]

model   = Inference(method=Inference.YAGER)
subs    = Subsets(slots=3, opts=[people, places, weapons])

# Witness #1.
model.add_mass(
    (Mass()
     .add(subs.new({2: ['spanner','lead-pipe', 'candlestick']}), 0.4)
     .add(subs.new({0: ['white','green','plum'], 1: ['lounge','study']}), 0.4)
     .add(subs.new(), 0.2)))

# Witness #2.
model.add_mass(
    (Mass()
     .add(subs.new({0: ['scarlett','plum'], 1: ['hall','study','library']}), 0.7)
     .add(subs.new(), 0.3)))

# Witness #3.
model.add_mass(
    (Mass()
     .add(subs.new({2: ['spanner', 'rope']}), 0.5)
     .add(subs.new({0: ['peacock','white','plum'], 1: ['kitchen','study','hall']}), 0.4)
     .add(subs.new(), 0.1)))


def calculate_and_print(q):
    belief, plausibility = model.approx(q, n=10000)
    print(q.schema(), belief, plausibility)

# Individuals.
for person in people:
    calculate_and_print(subs.new({0: [person]}))
print("")

# Places.
for place in places:
    calculate_and_print(subs.new({1: [place]}))
print("")

# Weapons.
for weapon in weapons:
    calculate_and_print(subs.new({2: [weapon]}))

print("")
# Plum investigation.
hypotheses = []
for place, weapon in product(places, weapons):
    q   = subs.new({0: ["plum"], 1: [place], 2: [weapon]})
    b,p = model.approx(q,n=10000)
    hypotheses.append((p, q.schema()))

for p, h in sorted(hypotheses, reverse=True)[:10]:
    print(p, h)
