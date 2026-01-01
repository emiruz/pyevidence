from collections import defaultdict
from pyevidence import *
import numpy as np
import unittest, itertools


class TestSubsets(unittest.TestCase):

    def test_make_subset(self):
        opts = [['a','b','c'], ['x','y'], ['i','j','k','l']]
        subs = Subsets(3, opts)
        sub  = list(subs.new().generate())
        sub0 = list(itertools.product(*opts))

        assert len(sub) == len(sub0) > 0
        assert sub == list(itertools.product(*opts))
        sub2 = list(subs.new({0: ['a']}).generate())
        assert sub2 == list(itertools.product(['a'],opts[1],opts[2]))

    def test_conj(self):
        opts = [['a','b','c'],['x','y'], ['z']]
        subs = Subsets(3, opts)
        sub  = subs.new().conj(subs.new({0: ['a'], 1: ['x','y']}))
        assert list(sub.generate()) == list(itertools.product(['a'],opts[1], opts[2]))

    def test_hull(self):
        opts = [['a','b','c']] * 3
        subs = Subsets(3, opts)
        sub  = subs.new({0: ['a']}).hull(subs.new({0: ['c'], 2: ['a','b']}))
        assert list(sub.generate()) == list(itertools.product(['a','c'], opts[0], opts[0]))

    def test_is_empty(self):
        opts = [['a','b','c'],['d','f'], ['x','y','z','w']]
        subs = Subsets(3, opts)
        sub1, sub2 = subs.new({0: ['a']}), subs.new({0: ['c']})
        assert sub1.conj(sub2).is_empty()

    def test_is_empty(self):
        opts = [['a','b','c'],['d','f'], ['x','y','z','w']]
        subs = Subsets(3, opts)
        assert subs.new().is_omega()
        assert not subs.new({0: ['a']}).is_omega()
        
    def test_implies(self):
        opts = [['a','b','c']] * 3
        subs = Subsets(3, opts)
        sub1 = subs.new({0: ['a','b']})
        sub2 = subs.new({0: ['a']})
        sub3 = subs.new({0: ['c']})
        assert sub2.implies(sub1)
        assert not sub3.implies(sub1)
        
    def test_intersects(self):
        opts = [['a','b','c'],['i','j','k','l']]
        subs = Subsets(2, opts)
        sub1 = subs.new({0: ['a','b'], 1: ['j','k']})
        sub2 = subs.new({0: ['a'], 1: ['j']})
        sub3 = subs.new({0: ['c']})
        assert sub1.intersects(sub2)
        assert sub3.intersects(subs.new())
        assert not sub2.intersects(sub3)
        assert not sub1.intersects(sub3)


if __name__ == "__main__":
    unittest.main()
