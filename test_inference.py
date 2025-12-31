from collections import defaultdict
from evidence import *
import unittest
import itertools
import copy


class TestInference(unittest.TestCase):

    def _exact_yager_three_state(self, masses):
        """
        Exact combination for the special 3-focal-element family:
          focal elements are {q, ¬q, Ω} only.
        Represent each mass by (a,b,u) where:
          a = m(q), b = m(¬q), u = m(Ω).
        Under Yager, conflict goes to Ω. Returns combined (a,b,u).
        """
        a, b, u = masses[0]
        for a_i, b_i, u_i in masses[1:]:
            a0, b0, u0 = a, b, u
            a = a0*a_i + a0*u_i + u0*a_i
            b = b0*b_i + b0*u_i + u0*b_i
            u = u0*u_i + a0*b_i + b0*a_i
        return a, b, u

    def test_coarse_is_exact_on_three_state_family(self):
        # 1 slot, 2 options => q and ¬q are complements; Ω is unconstrained.
        opts = ['a', 'b']
        subs = Subsets(1, opts)
        q    = subs.new({0: ['a']})
        nq   = subs.new({0: ['b']})  # ¬q within this 2-option universe
        omg  = subs.new()

        # Construct two sources with masses only on {q, ¬q, Ω}.
        m1 = Mass().add(q, 0.2).add(nq, 0.3).add(omg, 0.5)
        m2 = Mass().add(q, 0.6).add(nq, 0.1).add(omg, 0.3)

        infer = Inference(method=Inference.DP)  # coarse ignores method
        infer.add_mass(m1).add_mass(m2)

        b_coarse, p_coarse = infer.coarse(q)

        a_exact, b_exact, u_exact = self._exact_yager_three_state([(0.2, 0.3, 0.5),
                                                                   (0.6, 0.1, 0.3)])
        # In this family: Bel(q)=m(q)=a, Pl(q)=1-m(¬q)=1-b
        assert abs(b_coarse - a_exact) < 1e-12
        assert abs(p_coarse - (1 - b_exact)) < 1e-12
        assert 0 <= b_coarse <= p_coarse <= 1

    def test_coarse_order_invariant(self):
        opts = ['a', 'b']
        subs = Subsets(1, opts)
        q, nq, omg = subs.new({0: ['a']}), subs.new({0: ['b']}), subs.new()

        m1 = Mass().add(q, 0.25).add(nq, 0.25).add(omg, 0.50)
        m2 = Mass().add(q, 0.10).add(nq, 0.40).add(omg, 0.50)
        m3 = Mass().add(q, 0.70).add(nq, 0.10).add(omg, 0.20)

        infer1 = Inference().add_mass(m1).add_mass(m2).add_mass(m3)
        infer2 = Inference().add_mass(m1).add_mass(m3).add_mass(m2)

        b1, p1 = infer1.coarse(q)
        b2, p2 = infer2.coarse(q)

        assert abs(b1 - b2) < 1e-12
        assert abs(p1 - p2) < 1e-12

    def test_approx_converges_on_three_state_family(self):
        np.random.seed(0)
        opts = ['a', 'b']
        subs = Subsets(1, opts)
        q, nq, omg = subs.new({0: ['a']}), subs.new({0: ['b']}), subs.new()

        m1 = Mass().add(q, 0.2).add(nq, 0.3).add(omg, 0.5)
        m2 = Mass().add(q, 0.6).add(nq, 0.1).add(omg, 0.3)

        infer = Inference(method=Inference.YAGER).add_mass(m1).add_mass(m2)

        a_exact, b_exact, _ = self._exact_yager_three_state([(0.2, 0.3, 0.5),
                                                             (0.6, 0.1, 0.3)])
        bel_exact = a_exact
        pl_exact  = 1 - b_exact

        bel_hat, pl_hat = infer.approx(q, n=20000)

        assert abs(bel_hat - bel_exact) < 0.02
        assert abs(pl_hat - pl_exact) < 0.02
        assert 0 <= bel_hat <= pl_hat <= 1

    def test_approx_conflict_rule_difference(self):
        # Build two sources that always conflict (conjunction empty),
        # and choose q disjoint from BOTH, so DP plausibility=0 but Yager plausibility=1.
        opts = ['a', 'b', 'c']
        subs = Subsets(1, opts)

        A = subs.new({0: ['a']})
        B = subs.new({0: ['b']})
        q = subs.new({0: ['c']})  # disjoint from A and B

        m1 = Mass().add(A, 1.0)
        m2 = Mass().add(B, 1.0)

        np.random.seed(1)
        bel_dp, pl_dp = Inference(method=Inference.DP).add_mass(m1).add_mass(m2).approx(q, n=2000)

        np.random.seed(1)
        bel_yg, pl_yg = Inference(method=Inference.YAGER).add_mass(m1).add_mass(m2).approx(q, n=2000)

        assert bel_dp == 0.0 and pl_dp == 0.0
        assert bel_yg == 0.0 and pl_yg == 1.0

    def test_single_source_approx_matches_exact_bel_pl(self):
        np.random.seed(2)
        opts = ['a', 'b', 'c']
        subs = Subsets(2, opts)

        # Query q constrains slot0 to {a}; slot1 unconstrained.
        q = subs.new({0: ['a']})

        s1 = subs.new({0: ['a']})          # implies q
        s2 = subs.new({0: ['a', 'b']})     # intersects q but does not imply
        s3 = subs.new({0: ['c']})          # does not intersect q
        omg = subs.new()                   # Ω

        m = Mass().add(s1, 0.30).add(s2, 0.20).add(s3, 0.10).add(omg, 0.40)

        # Exact (single source):
        bel_exact = 0.30
        pl_exact  = 1 - 0.10

        infer = Inference().add_mass(m)
        bel_c, pl_c = infer.coarse(q)  # should equal exact for one source
        bel_a, pl_a = infer.approx(q, n=20000)

        assert abs(bel_c - bel_exact) < 1e-12
        assert abs(pl_c - pl_exact) < 1e-12
        assert abs(bel_a - bel_exact) < 0.02
        assert abs(pl_a - pl_exact) < 0.02
        assert 0 <= bel_a <= pl_a <= 1


    def test_approx_order_invariant(self):
        np.random.seed(3)
        opts = ['a', 'b', 'c']
        subs = Subsets(2, opts)

        q = subs.new({0: ['a'], 1: ['b']})

        A = subs.new({0: ['a']})
        B = subs.new({1: ['b', 'c']})
        C = subs.new({0: ['c'], 1: ['b']})

        m1 = Mass().add(A, 0.4).add(B, 0.6)
        m2 = Mass().add(B, 0.5).add(C, 0.5)
        m3 = Mass().add(A, 0.2).add(C, 0.8)

        infer1 = Inference().add_mass(m1).add_mass(m2).add_mass(m3)
        infer2 = Inference().add_mass(m3).add_mass(m1).add_mass(m2)

        bel1, pl1 = infer1.approx(q, n=20000)
        bel2, pl2 = infer2.approx(q, n=20000)

        assert abs(bel1 - bel2) < 1e-2
        assert abs(pl1  - pl2) < 1e-2
        assert 0 <= bel1 <= pl1 <= 1
