# pyevidence

This package implements some representations and algorithms from evidence
theory which are both generally useful and computationally efficient.

The `Subsets` and `Subset` classes encode subsets as a single bit vector
which enables efficient conjunction, hull, intersection and implication
but does not support disjunction or negation.

The `Mass` and `Inference` classes enable binary coarse inference using
Yager's rule, and both Yager and Dubois-Prade estimation via Monte Carlo.

Start with the blog post [here](https://emiruz.com/post/2026-01-03-pyevidence/)
which explains how it works and why.


## Contribution

1. Efficient bit vector representation of focal sets.

2. Efficient conjunction, hull, intersection and implication operators.

3. Efficient binary coarsening implementation of Yager's rule for
   calculating belief(Q)/plausibility(Q) given evidence.

4. Monte Carlo estimators for Yager and Dubois-Prade.


## Installation

```
python3 -m build
pip3 install dist/*.whl
```

## Usage

Start with the blog post [here](https://emiruz.com/post/2026-01-03-pyevidence/)
which explains how it works and why.

Also, see the following for an example application:

https://github.com/emiruz/qu-tagger

The tests provide some further examples.


## To-do

I think the performance could be improved by 2-5 times by porting this
implementation to typed Cython. I may do that if I run into an application
which requires it.
