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
