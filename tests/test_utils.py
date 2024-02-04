import unittest

from monad_std.utils import *


class TestUtils(unittest.TestCase):
    def test_cmp(self):
        o1 = cmp.Ordering.parse(cmp.Ordering.Less)
        o2 = cmp.Ordering.parse(-1)
        o3 = cmp.Ordering.parse(-4.2)
        self.assertTrue(o1 == o2 == o3)

        self.assertEqual(cmp.Ordering.from_cmp(0), cmp.Ordering.Equal)
        self.assertEqual(cmp.Ordering.from_cmp(1), cmp.Ordering.Greater)
        self.assertEqual(cmp.Ordering.from_cmp(-1), cmp.Ordering.Less)

        self.assertEqual(cmp.Ordering.from_num(0.0), cmp.Ordering.Equal)
        self.assertEqual(cmp.Ordering.from_num(1.5), cmp.Ordering.Greater)
        self.assertEqual(cmp.Ordering.from_num(-3.2), cmp.Ordering.Less)

        self.assertEqual(cmp.compare(0, 1), cmp.Ordering.Less)
        self.assertEqual(cmp.compare(5.0, -3), cmp.Ordering.Greater)
        self.assertEqual(cmp.compare(5, 5.0), cmp.Ordering.Equal)

        a = 0
        b = 1
        self.assertEqual(cmp.max_by(a, b, lambda x, y: cmp.compare(x, y)), b)
        self.assertEqual(cmp.max_by(a, b, lambda x, y: cmp.compare(y, x)), a)    # reverse the comparison here.
        self.assertEqual(-max(-a, -b), a)

        a = 0
        b = 1
        self.assertEqual(cmp.min_by(a, b, lambda x, y: cmp.compare(x, y)), a)
        self.assertEqual(cmp.min_by(a, b, lambda x, y: cmp.compare(y, x)), b)    # reverse the comparison here.
        self.assertEqual(-min(-a, -b), b)


if __name__ == '__main__':
    unittest.main()
