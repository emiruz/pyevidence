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
sub  = subs.new()

print(list(sub.generate()))

>> [('a', 'x'), ('a', 'y'), ('a', 'z'), ('b', 'x'), ('b', 'y'), ('b', 'z')]
```
If we wanted ot define a more specific subset we can specify what options
are available per slot:
```
sub2 = subs.new({0: ['a'], 1: ['x','z']})
print(list(sub2.generate()))

>> [('a', 'x'), ('a', 'z')]
```
The `sub.schema()` function will output a readable schema for each subset
so that it is easier to see what is going on.
```
print("default,",  sub.schema())
print("specific,", sub2.schema())

>> default,  * *
>> specific, {'a'} {'z', 'x'}
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

...
