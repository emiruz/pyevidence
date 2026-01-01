# pyevidence

This package implements some representations and algorithms from evidence
theory which are both generally useful and computationally efficient.

The `Subsets` and `Subset` classes encode subsets as a single bit vector
which enables efficient conjunction, hull, intersection and implication
but does not support disjunction or negation.

The `Mass` and `Inference` classes enable binary coarse inference using
Yager's rule, and both Yager and Dubois-Prade estimation via Monte Carlo.


## Contribution

1. Efficient bit vector representation of focal sets.

2. Efficient conjunction, hull, intersection and implication operators.

3. Efficient binary coarsening implementation of Yager's rule for
   calculating belief(Q)/plausibility(Q) given evidence.

4. Monte Carlo estimators for Yager and Dubois-Prade.


## Installation

```
pip3 install git+https://github.com/emiruz/pyevidence.git
```

## Usage

### Making subsets

Start by importing the `Subsets` class:

```
from pyevidence import Subsets
```

Sets are constructed by specifying how many slots/dimensions they have and
what the option in each dimension should be. For example, if we wanted to
define a set representing the Cartesian join {a,b} * {x,y,z} we would write:
```
subs = Subsets(slots=2, opts=[['a','b'], ['x','y','z']])
sub1 = subs.new()

print(list(sub1.generate()))

>> [('a', 'x'), ('a', 'y'), ('a', 'z'), ('b', 'x'), ('b', 'y'), ('b', 'z')]
```
If we wanted ot define a more specific subset we can specify what options
are available per slot:
```
sub2 = subs.new({0: ['a'], 1: ['x','z']})
print(list(sub2.generate()))

>> [('a', 'x'), ('a', 'z')]
```
The `sub1.schema()` function will output a readable schema for each subset
so that it is easier to see what is going on.
```
print("sub1,", sub1.schema())
print("sub2,", sub2.schema())

>> sub1, * *
>> sub2, {'a'} {'z', 'x'}
```
Cartesian joins are the representational limitation of this package. It
enables otherwise large subsets to be represented as a small set of integers
and for all operations to be bitwise comparisons: linear time/space complexity.


### Mass assignment

Start by importing the `Mass` class:
```
from pyevidence import Subsets, Mass
```
Once we've made some subsets, we can create a mass function by adding the
subset and a probability assignment to a `Mass` object:
```
mass = Mass()
mass.add(sub1, 0.1)
mass.add(sub2, 0.7)
mass.add(sub3, 0.2)
```
The assignment should add up to 1. We can check this by running
`mass.is_valid()`.


### Inference

Start by importing the `Inference` class:
```
from pyevidence import Subsets, Mass, Inference
```
The inference class enables inference over fused mass functions. That is,
queries for subsets over masses considered together. It supports two 
fusion rules which differ in how they handle disagreements between mass
assigments. Setting `method=Inference.YAGER` assigns disagreement to the
vacuous set (ignorance) whilst `method=Inference.DP` assigns it to the 
disjunction of the terms which disagree. For example:
```
model = Inference(method=Inference.YAGER)
```
Once the method is declared we can add mass assignments like so:
```
model.add_mass(mass1)
model.add_mass(mass2)
...
```
There are two functions which we can use to calculate belief/plausibility
for some subset `q`. The `coarse` function will reduce your mass
assignments to the simpler focal set of `{q, not q}` and then perform a
binary mass fusion which has identical for both methods. The benefit of
the function is efficiency however making the focal set more coarse will
lose information and make inference approximate, the effect of which
increases with the granularity of your full focal set and the number of
mass assignments.

The alternative is to use `approx` which is a Monte Carlo estimation of
the exact inference. The benefits are that the full granularity of your
focal set will be taken into account, and time complexity will scale
linearly with the number of mass assigments, however granular focal sets
with many assignments require many simulations, so the constants can be
large. Here is the format:
```
b1, p1 = model.coarse(q)          # Coarse inference.
b2, p2 = model.approx(q, n=10000) # Monte Carlo estimation.
```

### A "whodunit" example
Here is a short Cluedo themed example in which we combine uncertain set
based evidence from three witnesses to infer "whodunit".
```
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

# Places.
for place in places:
    calculate_and_print(subs.new({1: [place]}))

# Weapons.
for weapon in weapons:
    calculate_and_print(subs.new({2: [weapon]}))


> {'plum'} * *          0.4450 1.0
> {'scarlett'} * *      0.0    0.3606
> {'mustard'} * *       0.0    0.1094
> {'white'} * *         0.0    0.2973
> {'green'} * *         0.0    0.1778
> {'peacock'} * *       0.0    0.1791

> * {'kitchen'} *       0.0    0.1796
> * {'ballroom'} *      0.0    0.1084
> * {'conservatory'} *  0.0    0.1097
> * {'dining room'} *   0.0    0.1076
> * {'billiard room'} * 0.0    0.1067
> * {'library'} *       0.0    0.3587
> * {'lounge'} *        0.0    0.1800
> * {'hall'} *          0.0    0.5990
> * {'study'} *         0.3279 1.0

> * * {'candlestick'}   0.0    0.5086
> * * {'dagger'}        0.0    0.3009
> * * {'lead-pipe'}     0.0    0.5029
> * * {'revolver'}      0.0    0.3010
> * * {'rope'}          0.0    0.6002
> * * {'spanner'}       0.1975 1.0
```
From the above results, we believe that `plum` was the most
likely antagonist, the `study` the most likely location and
a `spanner` the most likely weapon. Meanwhile, plausibility
(a measure of non-contradiction) suggests `mustard` is the
suspect least supported by the evidence. Let's investigate
`plum` some more. We do no have much evidence for combined
beliefs about how and where `plum` might have done it, but
we can examine where the evidence is least contradictory.
Here are the top 10 hypotheses by plausibility:
```
hypotheses = []
for place, weapon in product(places, weapons):
    q   = subs.new({0: ["plum"], 1: [place], 2: [weapon]})
    b,p = model.approx(q,n=10000)
    hypotheses.append((p, q.schema()))

for p, h in sorted(hypotheses, reverse=True)[:10]:
    print(p, h)


> 1.0     {'plum'}  {'study'}   {'spanner'}
> 0.6044  {'plum'}  {'study'}   {'rope'}
> 0.5974  {'plum'}  {'hall'}    {'spanner'}
> 0.5084  {'plum'}  {'study'}   {'lead-pipe'}
> 0.5005  {'plum'}  {'study'}   {'candlestick'}
> 0.3556  {'plum'}  {'library'} {'spanner'}
> 0.3068  {'plum'}  {'hall'}    {'candlestick'}
> 0.3054  {'plum'}  {'study'}   {'revolver'}
> 0.2979  {'plum'}  {'hall'}    {'lead-pipe'}
> 0.2954  {'plum'}  {'study'}   {'dagger'}
```
So, most plausibly `plum` in the `study` with a `spanner`
according to our uncertain witnesses.
