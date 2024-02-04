import unittest

from monad_std.std_types import MList, MTuple, MDict, MSet
from monad_std import Option


class TestStdType(unittest.TestCase):
    def test_list(self):
        x = MList([1, 2, 3, 4, 5])
        self.assertEqual(x.index(2), Option.some(1))
        self.assertEqual(x.index(0), Option.none())
        self.assertEqual(x.get(2), Option.some(3))
        self.assertEqual(x.get(10), Option.none())

        x = MList([1, 2, 3, 4, 5])
        self.assertEqual(x.pop(), Option.some(5))
        self.assertEqual(x.pop(1), Option.some(2))
        x = MList()
        self.assertEqual(x.pop(), Option.none())

    def test_tuple(self):
        x = MTuple((1, 3, "hey"))
        self.assertEqual(x.index("hey"), Option.some(2))
        self.assertEqual(x.index("hello"), Option.none())
        self.assertEqual(x.get(1), Option.some(3))
        self.assertEqual(x.get(5), Option.none())

    def test_dict(self):
        x = MDict({"a": 1, "b": 2, "c": 3})
        self.assertEqual(x.get("b"), Option.some(2))
        self.assertEqual(x.get("d"), Option.none())

        x = MDict({"a": 1})
        self.assertEqual(x.popitem(), Option.some(("a", 1)))
        self.assertEqual(x.popitem(), Option.none())

        x = MDict({"a": 1})
        self.assertEqual(x.pop("a"), Option.some(1))
        self.assertEqual(x.pop("b"), Option.none())
        self.assertEqual(x.pop("a"), Option.none())

    def test_set(self):
        x = MSet([1, "d"])
        p1 = x.pop()
        self.assertTrue(p1 == Option.some(1) or p1 == Option.some("d"))
        x.pop()
        self.assertEqual(x.pop(), Option.none())


if __name__ == "__main__":
    unittest.main()
