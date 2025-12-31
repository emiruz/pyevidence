from collections import defaultdict
from evidence import *
import unittest
import itertools
import copy


class TestSubsets(unittest.TestCase):

    def test_make_subset(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub  = list(subs.new().generate())
        assert sub == list(itertools.product(opts,opts,opts))
        sub2 = list(subs.new({0: ['a']}).generate())
        assert sub2 == list(itertools.product(['a'],opts,opts))

    def test_conj(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub  = subs.new().conj(subs.new({0: ['a'], 2: ['a','b']}))
        assert list(sub.generate()) == list(itertools.product(['a'],opts,['a','b']))

    def test_hull(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub  = subs.new({0: ['a']}).hull(subs.new({0: ['c'], 2: ['a','b']}))
        assert list(sub.generate()) == list(itertools.product(['a','c'], opts, opts))

    def test_is_empty(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub1, sub2 = subs.new({0: ['a']}), subs.new({0: ['c']})
        assert sub1.conj(sub2).is_empty()

    def test_implies(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub1 = subs.new({0: ['a','b']})
        sub2 = subs.new({0: ['a']})
        sub3 = subs.new({0: ['c']})
        assert sub2.implies(sub1)
        assert not sub3.implies(sub1)
        
    def test_intersects(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub1 = subs.new({0: ['a','b']})
        sub2 = subs.new({0: ['a']})
        sub3 = subs.new({0: ['c']})
        assert sub1.intersects(sub1)
        assert sub3.intersects(subs.new())
        assert not sub2.intersects(sub3)
        assert not sub1.intersects(sub3)


class TestMass(unittest.TestCase):

    def test_make_mass_and_sample(self):
        opts = ['a','b','c']
        subs = Subsets(3, opts)
        sub1 = subs.new({0: ['a','b']})
        sub2 = subs.new({0: ['a']})
        sub3 = subs.new({0: ['c']})

        mass = Mass()
        mass.add(sub1, 0.1)
        mass.add(sub2, 0.7)
        mass.add(sub3, 0.2)

        assert len(mass.mass) == 3
        assert mass.is_valid()

        samples = defaultdict(lambda: 0)
        for _ in range(10000):
            x = mass.sample()[0]
            samples[tuple(x.bits)] += 1

        samples = sorted([(n,k,) for k,n in samples.items()])
        assert [tuple(sub1.bits), tuple(sub3.bits), tuple(sub2.bits)] \
            == [k for _, k in samples]


class TestInference(unittest.TestCase):

    def test_query_simple(self):
        opts  = ['a','b','c']
        subs  = Subsets(3, opts)
        sub1  = subs.new({0: ['a','b']})
        sub2  = subs.new({0: ['a']})
        sub3  = subs.new({0: ['c']})
        mass1 = Mass()
        mass1.add(sub1, 0.1); mass1.add(sub2, 0.7); mass1.add(sub3, 0.2)
        infer = Inference(method="dubois-prade")
        infer.add_mass(mass1)
        b0, p0 = infer.coarse(sub3)
        b1, p1 = infer.approx(sub3, n=2000)
        assert abs(b0 - 0.2) < 1e-8 and abs(p0 - 0.2) < 1e-8
        assert 0.15 < b1 < 0.25 and 0.15 < p1 < 0.25

    def test_query_two_source(self):
        opts  = ['a','b','c']
        subs  = Subsets(3, opts)
        sub1  = subs.new({0: ['a','b']})
        sub2  = subs.new({1: ['b','c']})
        sub3  = subs.new({2: ['c']})
        mass1 = Mass()
        mass1.add(sub1, 0.3); mass1.add(sub2, 0.2); mass1.add(sub3, 0.5)
    
        sub4  = subs.new({0: ['c']})
        sub5  = subs.new({1: ['b','c']})
        sub6  = subs.new({2: ['a','b']})
        mass2 = Mass()

        mass2.add(sub4, 0.7); mass2.add(sub5, 0.2); mass2.add(sub6, 0.10)

        infer = Inference(method="dubois-prade")
        infer.add_mass(mass1)
        b0, p0 = infer.coarse(sub3)
        b1, p1 = infer.approx(sub3, n=2000)
        assert b0 == 0.5 and p0 ==1
        assert 0.45 < b1 < 0.55 and p1 == 1

if __name__ == "__main__":
    unittest.main()
