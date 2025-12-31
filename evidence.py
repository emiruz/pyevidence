from functools import reduce
from itertools import product
import random
import numpy as np


class Subset:
    """Bitset-encoded constraints over `slots`, each slot is a subset of `opts`."""

    def __init__(self, parent, settings, slots, opts, default):
        """Build per-slot bitmasks from `settings` (slot index -> allowed options)."""
        assert isinstance(parent, Subsets) and \
            isinstance(opts, list) and \
            isinstance(settings, dict) and \
            isinstance(default, int)
        self.parent = parent
        self.slots = slots
        self.default = default
        self.opts = opts
        self.bits = [default] * slots

        f = lambda a, b: a | b  # bitwise union across option masks

        for i, Os in settings.items():
            assert isinstance(Os, list)
            assert all(o in opts for o in Os)
            if Os == []:
                self.bits[i] = default  # treat empty list as "no constraint" (Ω) for that slot
            else:
                self.bits[i] = reduce(f, (2**opts.index(o) for o in Os))  # allowed options -> mask

    def conj(self, s0):
        """Conjunction (intersection) of constraints: per-slot bitwise AND."""
        self.bits = [a & b for a, b in zip(self.bits, s0.bits)]
        return self

    def hull(self, s0):
        """Disjunction/upper hull (union) of constraints: per-slot bitwise OR."""
        self.bits = [a | b for a, b in zip(self.bits, s0.bits)]
        return self

    def is_empty(self):
        """True iff any slot has no allowed options (mask = 0)."""
        return any(x == 0 for x in self.bits)

    def is_omega(self):
        """True iff all slots are unconstrained (mask = default = all 1s)."""
        return all(x == self.default for x in self.bits)

    def implies(self, s0):
        """Subset implication: every slot's mask is contained in s0's mask."""
        return all(a & b == a for a, b in zip(self.bits, s0.bits))

    def intersects(self, s0):
        """Non-empty intersection per slot: all slotwise ANDs are nonzero."""
        return all(a & b != 0 for a, b in zip(self.bits, s0.bits))

    def __to_opts(self, x):
        """Decode a bitmask into the corresponding list of option labels."""
        assert isinstance(x, int)
        pos = [(i, 2**y) for i, y in enumerate(range(len(self.opts)))]
        return [self.opts[i] for i, y in pos if x & y == y]

    def generate(self):
        """Enumerate all assignments consistent with this subset (Cartesian product)."""
        return product(*[self.__to_opts(x) for x in self.bits])

    def schema(self):
        """Human-readable per-slot constraint schema (`*` for unconstrained)."""
        xs = [self.__to_opts(x) for x in self.bits]
        xs = ['*' if x == self.opts else str(set(x)) for x in xs]
        return " ".join(xs)


class Subsets:
    """Factory/namespace for Subset objects with fixed `slots` and `opts`."""

    slots, opts, default = None, None, None

    def __init__(self, slots, opts):
        """Define the universe: number of slots and option alphabet per slot."""
        assert isinstance(opts, list) and len(opts) > 0 and slots > 0
        self.opts = opts
        self.slots = slots
        self.default = int("".join(["1"] * len(opts)), 2)  # all options allowed (Ω mask)

    def new(self, settings=dict()):
        """Create a new Subset with given per-slot constraints."""
        assert isinstance(settings, dict)
        return Subset(self, settings, self.slots, self.opts, self.default)


class Mass:
    """A basic probability mass function over Subset focal elements (must sum to 1)."""

    def __init__(self):
        """Initialize empty mass assignment."""
        self.P = 0.0
        self.mass = []
        self.probs = []

    def add(self, s0, p):
        """Add focal element `s0` with mass `p`, tracking total mass."""
        assert isinstance(s0, Subset) and 0 <= p <= 1
        assert self.P + p <= 1 + 1e-8
        self.mass.append(s0)
        self.probs.append(p)
        self.P += p
        return self

    def is_valid(self):
        """Check normalization (total mass ≈ 1)."""
        assert abs(self.P - 1.0) <= 1e-8
        return True

    def sample(self, k=1):
        """Sample focal elements according to their masses."""
        return np.random.choice(self.mass, p=self.probs, size=k)


class Inference:
    """Combine multiple mass functions and query belief/plausibility for a Subset."""

    YAGER, DP = "yager", "dubois-prade"

    def __init__(self, method=DP):
        """Select conflict handling rule for approximation (Yager vs Dubois–Prade)."""
        assert method in (Inference.YAGER, Inference.DP)
        self.mass = []
        self.method = method

    def add_mass(self, m):
        """Register a normalized mass function."""
        assert isinstance(m, Mass)
        m.is_valid()
        self.mass.append(m)
        return self

    def coarse(self, q):
        """Approximate belief/plausibility bounds via iterative combination of (a,b,u)."""
        assert isinstance(q, Subset) and len(self.mass) > 0
        assert not q.is_empty() and not q.is_omega()

        As = [sum(p for x, p in zip(mm.mass, mm.probs) if x.implies(q)) for mm in self.mass]       # support for q
        Bs = [sum(p for x, p in zip(mm.mass, mm.probs) if not x.intersects(q)) for mm in self.mass] # support for ¬q

        a, b = As[0], Bs[0]
        u = 1 - a - b  # residual/ignorance mass

        if len(As) == 1:
            return a, 1 - b

        for a_i, b_i in zip(As[1:], Bs[1:]):
            u_i = 1 - a_i - b_i
            a0, b0, u0 = a, b, u
            a = a0*a_i + a0*u_i + u0*a_i
            b = b0*b_i + b0*u_i + u0*b_i
            u = u0*u_i + a0*b_i + b0*a_i

        return a, 1 - b

    def approx(self, q, n=999):
        """Monte Carlo estimate of belief/plausibility under random sampling."""
        assert isinstance(q, Subset) and len(self.mass) > 0
        assert not q.is_empty() and not q.is_omega()
        belief, plausibility = 0, 0

        Es = [m.sample(k=n) for m in self.mass]  # iid samples per source mass function
        f = lambda a, b: a.conj(b)               # combine samples by conjunction

        for j in range(n):
            E = [x[j] for x in Es]
            S = reduce(f, E, q.parent.new())     # conjunct all sampled focal elements

            if not S.is_empty():
                belief += 1 if S.implies(q) else 0
                plausibility += 1 if S.intersects(q) else 0
            else:
                # conflict resolution when combined sample is empty
                if self.method == Inference.YAGER:
                    plausibility += 1
                else:
                    belief += 1 if all(s.implies(q) for s in E) else 0
                    plausibility += 1 if any(e.intersects(q) for e in E) else 0

        return belief / n, plausibility / n
