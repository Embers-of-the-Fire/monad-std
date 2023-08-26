import unittest

from monad_std.std_types import MList, MTuple, MDict, MSet
from monad_std import Option


class TestStdList(unittest.TestCase):
    def test_index(self):
        x = MList([1, 2, 3, 4, 5])
        self.assertEqual(x.index(2), Option.of_some(1))
        self.assertEqual(x.index(0), Option.of_none())
        self.assertEqual(x.get(2), Option.of_some(3))
        self.assertEqual(x.get(10), Option.of_none())

    def test_pop(self):
        x = MList([1, 2, 3, 4, 5])
        self.assertEqual(x.pop(), Option.of_some(5))
        self.assertEqual(x.pop(1), Option.of_some(2))
        x = MList()
        self.assertEqual(x.pop(), Option.of_none())


class TestStdTuple(unittest.TestCase):
    def test_index(self):
        x = MTuple((1, 3, 'hey'))
        self.assertEqual(x.index('hey'), Option.of_some(2))
        self.assertEqual(x.index('hello'), Option.of_none())
        self.assertEqual(x.get(1), Option.of_some(3))
        self.assertEqual(x.get(5), Option.of_none())


class TestStdDict(unittest.TestCase):
    def test_index(self):
        x = MDict({'a': 1, 'b': 2, 'c': 3})
        self.assertEqual(x.get('b'), Option.of_some(2))
        self.assertEqual(x.get('d'), Option.of_none())

    def test_pop(self):
        x = MDict({'a': 1})
        self.assertEqual(x.popitem(), Option.of_some(('a', 1)))
        self.assertEqual(x.popitem(), Option.of_none())

        x = MDict({'a': 1})
        self.assertEqual(x.pop('a'), Option.of_some(1))
        self.assertEqual(x.pop('b'), Option.of_none())
        self.assertEqual(x.pop('a'), Option.of_none())


class TestStdSet(unittest.TestCase):
    def test_index(self):
        x = MSet([1, 'd'])
        p1 = x.pop()
        self.assertTupleEqual(p1 == Option.of_some(1) or p1 == Option.of_some('d'))
        x.pop()
        self.assertEqual(x.pop(), Option.of_none())


if __name__ == '__main__':
    unittest.main()
