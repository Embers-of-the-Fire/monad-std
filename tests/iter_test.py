import unittest
import funct

from monad_std.iter import IterMeta
from monad_std import Option, Result


class ResultTest(unittest.TestCase):
    def test_iter(self):
        t = IterMeta.iter(range(10))
        self.assertListEqual(t.collect_list(), list(range(10)))
        t = IterMeta.iter(range(10))
        self.assertTupleEqual(t.collect_tuple(), tuple(range(10)))
        t = IterMeta.iter(range(10))
        self.assertEqual(t.collect_string(), "".join(map(str, range(10))))
        t = IterMeta.iter(range(10))
        self.assertEqual(t.collect_array(), funct.Array(range(10)))
        t = IterMeta.iter(range(10))
        self.assertEqual(t.count(), 10)

    def test_iter_enumerator(self):
        a = ["a", "b", "c"]
        it = IterMeta.iter(a).enumerate()
        self.assertEqual(it.next(), Option.of_some((0, "a")))
        self.assertEqual(it.next(), Option.of_some((1, "b")))
        self.assertEqual(it.next(), Option.of_some((2, "c")))
        self.assertEqual(it.next(), Option.of_none())

    def test_iter_filter(self):
        a = [-1, 0, 1, 2]
        it = IterMeta.iter(a)
        self.assertListEqual(it.filter(lambda x: x > 0).collect_list(), [1, 2])

    def test_iter_filter_map(self):
        a = ["1", "two", "3.0", "four", "5"]
        it1 = IterMeta.iter(a).filter_map(lambda x: Result.catch_from(float, x).ok())
        it2 = (
            IterMeta.iter(a)
            .map(lambda x: Result.catch_from(float, x))
            .filter(lambda x: x.is_ok())
            .map(lambda x: x.unwrap())
        )

        self.assertListEqual(it1.collect_list(), it2.collect_list())

    def test_iter_flatten(self):
        a = [[1, 2, 3, 4], [5, 6]]
        ftd = IterMeta.iter(a).flatten().collect_list()
        self.assertListEqual(ftd, [1, 2, 3, 4, 5, 6])

        words = ["alpha", "beta", "gamma"]
        ftd = IterMeta.iter(words).map(iter).flatten().collect_string()
        self.assertEqual(ftd, "alphabetagamma")

        a = [Option.of_some(123), Result.of_ok(321), Option.of_none(), Option.of_some(233), Result.of_err("err")]
        ftd = IterMeta.iter(a).flatten().collect_list()
        self.assertListEqual(ftd, [123, 321, 233])

        words = ["alpha", "beta", "gamma"]
        merged = IterMeta.iter(words).flat_map(iter).collect_string()
        self.assertEqual(merged, "alphabetagamma")

    def test_iter_fuse(self):
        class NullableIterator(IterMeta[int]):
            __state: int

            def __init__(self, state: int):
                self.__state = state

            def next(self):
                val = self.__state
                self.__state += 1
                if val % 2 == 0:
                    return Option.of_some(val)
                else:
                    return Option.of_none()

        it1 = NullableIterator(0)
        self.assertEqual(it1.next(), Option.of_some(0))
        self.assertEqual(it1.next(), Option.of_none())
        self.assertEqual(it1.next(), Option.of_some(2))
        self.assertEqual(it1.next(), Option.of_none())
        it2 = it1.fuse()
        self.assertEqual(it2.next(), Option.of_some(4))
        self.assertEqual(it2.next(), Option.of_none())
        self.assertEqual(it2.next(), Option.of_none())

    def test_iter_inspect(self):
        a = [1, 4, 2, 3]
        sumed = (IterMeta.iter(a)
               .inspect(lambda x: None)
               .filter(lambda x: x % 2 == 0)
               .inspect(lambda x: None)
               .fold(0, lambda acc, x: acc + x))
        self.assertEqual(sumed, 6)

    def test_iter_intersperse(self):
        it = IterMeta.iter([0, 1, 2]).intersperse(100)
        self.assertEqual(it.next(), Option.of_some(0))
        self.assertEqual(it.next(), Option.of_some(100))
        self.assertEqual(it.next(), Option.of_some(1))
        self.assertEqual(it.next(), Option.of_some(100))
        self.assertEqual(it.next(), Option.of_some(2))
        self.assertEqual(it.next(), Option.of_none())

        hello = IterMeta.iter(["Hello", "World", "!"]).intersperse(' ').collect_string()
        self.assertEqual(hello, "Hello World !")

        src = IterMeta.iter(["Hello", "to", "all", "people", "!!"])
        happy_emojis = IterMeta.iter([" ❤️ ", " 😀 "])
        separator = lambda: happy_emojis.next().unwrap_or(" 🦀 ")
        result = src.intersperse_with(separator).collect_string()
        self.assertEqual(result, "Hello ❤️ to 😀 all 🦀 people 🦀 !!")

    # noinspection PyMethodMayBeStatic
    def test_iter_for_each(self):
        (IterMeta.iter(range(5)).flat_map(lambda x: range(x * 100, x * 110))
         .enumerate()
         .filter(lambda d: (d[0] + d[1]) % 3 == 0)
         .for_each(lambda d: None))

    def test_iter_map(self):
        t = IterMeta.iter(range(10))
        self.assertListEqual(
            t.map(lambda x: x * 2).filter(lambda x: x % 3 == 1).enumerate().collect_list(),
            list(enumerate(filter(lambda x: x % 3 == 1, map(lambda x: x * 2, range(10))))),
        )
        a = [1, 2, 3]
        it = IterMeta.iter(a).map(lambda x: x * 2)
        self.assertEqual(it.next(), Option.of_some(2))
        self.assertEqual(it.next(), Option.of_some(4))
        self.assertEqual(it.next(), Option.of_some(6))
        self.assertEqual(it.next(), Option.of_none())

    def test_iter_peek(self):
        xs = [1, 2, 3]
        it = IterMeta.iter(xs).peekable()
        self.assertEqual(it.peek(), Option.of_some(1))
        self.assertEqual(it.next(), Option.of_some(1))
        self.assertEqual(it.peek(), Option.of_some(2))
        self.assertEqual(it.peek(), Option.of_some(2))
        self.assertEqual(it.next(), Option.of_some(2))
        self.assertEqual(it.next(), Option.of_some(3))
        self.assertEqual(it.peek(), Option.of_none())
        self.assertEqual(it.next(), Option.of_none())

    def test_iter_fold(self):
        a = [1, 2, 3]
        it = IterMeta.iter(a)
        self.assertEqual(it.fold(0, lambda acc, x: acc + x), 6)

        numbers = [1, 2, 3, 4, 5]
        result = IterMeta.iter(numbers).fold("0", lambda acc, x: f"({acc} + {x})")
        self.assertEqual(result, "(((((0 + 1) + 2) + 3) + 4) + 5)")

    def test_iter_index(self):
        a = [1, 2, 3]
        self.assertEqual(IterMeta.iter(a).find(lambda x: x == 2), Option.of_some(2))
        self.assertEqual(IterMeta.iter(a).find(lambda x: x == 5), Option.of_none())

        a = ["lol", "wow", "2", "5"]
        res = IterMeta.iter(a).find_map(lambda x: Result.catch_from(int, x).ok())
        self.assertEqual(res, Option.of_some(2))

        a = [1, 2, 3]

        self.assertTrue(IterMeta.iter(a).exist(2))
        self.assertFalse(IterMeta.iter(a).exist(5))

        self.assertEqual(IterMeta.iter(a).position(lambda x: x == 2), Option.of_some(1))
        self.assertEqual(IterMeta.iter(a).position(lambda x: x == 5), Option.of_none())

        self.assertEqual(IterMeta.iter(a).index(2), Option.of_some(1))
        self.assertEqual(IterMeta.iter(a).index(5), Option.of_none())

    def test_iter_reduce(self):
        reduced = IterMeta.iter(range(10)).reduce(lambda acc, e: acc + e)
        self.assertEqual(reduced, Option.of_some(45))
        self.assertEqual(reduced.unwrap(), IterMeta.iter(range(10)).fold(0, lambda acc, e: acc + e))

        a = [1, 2, 3]
        self.assertEqual(IterMeta.iter(a).sum(), Option.of_some(6))

        self.assertEqual(IterMeta.iter(range(1, 6)).product(), Option.of_some(120))
        self.assertEqual(IterMeta.iter(range(1, 1)).product(), Option.of_none())

    def test_iter_zip(self):
        a1 = [1, 3, 5]
        a2 = [2, 4, 6]
        it = IterMeta.iter(a1).zip(IterMeta.iter(a2))
        self.assertEqual(it.next(), Option.of_some((1, 2)))
        self.assertEqual(it.next(), Option.of_some((3, 4)))
        self.assertEqual(it.next(), Option.of_some((5, 6)))
        self.assertEqual(it.next(), Option.of_none())

    def test_iter_chain(self):
        element = 1
        it = IterMeta.once(element)
        self.assertEqual(it.next(), Option.of_some(1))
        self.assertEqual(it.next(), Option.of_none())

        a1 = [1, 3, 5]
        a2 = [2, 4, 6]
        it1 = IterMeta.iter(a1)
        it2 = IterMeta.iter(a2)
        self.assertListEqual(it1.chain(it2).collect_list(), [1, 3, 5, 2, 4, 6])

    def test_remain(self):
        a = [1, 2, 3, 4, 5]
        it = IterMeta.iter(a)
        it.next()
        it.next()
        self.assertListEqual(it.remain().collect_list(), [3, 4, 5])
        self.assertListEqual(it.collect_list(), [])

    def test_iter_chunk(self):
        a = IterMeta.iter("loerm").array_chunk(2)
        self.assertEqual(a.next(), Option.of_some(["l", "o"]))
        self.assertEqual(a.next(), Option.of_some(["e", "r"]))
        self.assertEqual(a.next(), Option.of_none())
        self.assertListEqual(a.get_unused().unwrap(), ["m"])


if __name__ == "__main__":
    unittest.main()
