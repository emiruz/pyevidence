from collections import defaultdict
from pyevidence import *
import numpy as np
import unittest, itertools


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

if __name__ == "__main__":
    unittest.main()
