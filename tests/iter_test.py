import unittest
import typing as t

import funct

from monad_std.prelude import *
from monad_std.iter import IterMeta
from monad_std import utils as mutils

from .testutil import *


class ResultTest(unittest.TestCase):
    def test_iter(self):
        t = siter(range(10))
        self.assertListEqual(t.collect_list(), list(range(10)))
        t = siter(range(10))
        self.assertTupleEqual(t.collect_tuple(), tuple(range(10)))
        t = siter(range(10))
        self.assertEqual(t.collect_string(), "".join(map(str, range(10))))
        t = siter(range(10))
        self.assertEqual(t.collect_array(), funct.Array(range(10)))
        t = siter(range(10)).chain(siter(range(2, 12)))
        self.assertSetEqual(t.collect_set(), set(range(12)))

        t = siter(range(5))
        lst = [1]
        t.collect_to_seq(lst)
        self.assertListEqual(lst, [1, 0, 1, 2, 3, 4])
        t = siter(range(5))
        uset = {0, 10}
        t.collect_to_set(uset)
        self.assertSetEqual(uset, {0, 1, 2, 3, 4, 10})
        t = siter(range(2, 5)).map(lambda x: (x, str(x + 1)))
        umap = {0: "1", 1: "2"}
        t.collect_to_map(umap)
        self.assertDictEqual(umap, {0: "1", 1: "2", 2: "3", 3: "4", 4: "5"})

        t = siter(range(10))
        self.assertEqual(t.count(), 10)

        a = [1, 2, 3, 4]
        it = siter(a)
        self.assertEqual(it.advance_by(2), Result.of_ok(None))
        self.assertEqual(it.next(), Option.some(3))
        self.assertEqual(it.advance_by(0), Result.of_ok(None))
        self.assertEqual(it.advance_by(100), Result.of_err(99))

        a = [1, 2, 3]
        self.assertEqual(siter(a).nth(1), Option.some(2))
        a = [1, 2, 3]
        self.assertEqual(siter(a).nth(10), Option.none())

        a = [1, 2, 3]
        self.assertEqual(siter(a).last(), Option.some(3))
        a = []
        self.assertEqual(siter(a).last(), Option.none())

        a = [1, 2, 3]
        it = siter(a)
        self.assertEqual(it.next_chunk(2), Ok([1, 2]))
        self.assertEqual(it.next_chunk(2), Err([3]))
        quote = "not all those who wander are lost"
        first, second, third = siter(quote.split(' ')).next_chunk(3).unwrap()
        self.assertEqual(first, 'not')
        self.assertEqual(second, 'all')
        self.assertEqual(third, 'those')

    def test_iter_enumerator(self):
        a = ["a", "b", "c"]
        it = siter(a).enumerate()
        self.assertEqual(it.next(), Option.some((0, "a")))
        self.assertEqual(it.next(), Option.some((1, "b")))
        self.assertEqual(it.next(), Option.some((2, "c")))
        self.assertEqual(it.next(), Option.none())

    def test_iter_filter(self):
        a = [-1, 0, 1, 2]
        it = siter(a)
        self.assertListEqual(it.filter(lambda x: x > 0).collect_list(), [1, 2])

    def test_iter_filter_map(self):
        a = ["1", "two", "3.0", "four", "5"]
        it1 = siter(a).filter_map(lambda x: Result.catch_from(float, x).ok())
        it2 = (
            siter(a)
            .map(lambda x: Result.catch_from(float, x))
            .filter(lambda x: x.is_ok())
            .map(lambda x: x.unwrap())
        )

        self.assertListEqual(it1.collect_list(), it2.collect_list())

    def test_iter_flatten(self):
        a = [[1, 2, 3, 4], [5, 6]]
        ftd = siter(a).flatten().collect_list()
        self.assertListEqual(ftd, [1, 2, 3, 4, 5, 6])

        words = ["alpha", "beta", "gamma"]
        ftd = siter(words).map(iter).flatten().collect_string()
        self.assertEqual(ftd, "alphabetagamma")

        a = [Option.some(123), Result.of_ok(321), Option.none(), Option.some(233), Result.of_err("err")]
        ftd = siter(a).flatten().collect_list()
        self.assertListEqual(ftd, [123, 321, 233])

        words = ["alpha", "beta", "gamma"]
        merged = siter(words).flat_map(iter).collect_string()
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
                    return Option.some(val)
                else:
                    return Option.none()

        it1 = NullableIterator(0)
        self.assertEqual(it1.next(), Option.some(0))
        self.assertEqual(it1.next(), Option.none())
        self.assertEqual(it1.next(), Option.some(2))
        self.assertEqual(it1.next(), Option.none())
        it2 = it1.fuse()
        self.assertEqual(it2.next(), Option.some(4))
        self.assertEqual(it2.next(), Option.none())
        self.assertEqual(it2.next(), Option.none())

    def test_iter_inspect(self):
        a = [1, 4, 2, 3]
        sumed = (siter(a)
                 .inspect(lambda x: None)
                 .filter(lambda x: x % 2 == 0)
                 .inspect(lambda x: None)
                 .fold(0, lambda acc, x: acc + x))
        self.assertEqual(sumed, 6)

    def test_iter_intersperse(self):
        it = siter([0, 1, 2]).intersperse(100)
        self.assertEqual(it.next(), Option.some(0))
        self.assertEqual(it.next(), Option.some(100))
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(it.next(), Option.some(100))
        self.assertEqual(it.next(), Option.some(2))
        self.assertEqual(it.next(), Option.none())

        hello = siter(["Hello", "World", "!"]).intersperse(' ').collect_string()
        self.assertEqual(hello, "Hello World !")

        src = siter(["Hello", "to", "all", "people", "!!"])
        happy_emojis = siter([" ❤️ ", " 😀 "])
        separator = lambda: happy_emojis.next().unwrap_or(" 🦀 ")
        result = src.intersperse_with(separator).collect_string()
        self.assertEqual(result, "Hello ❤️ to 😀 all 🦀 people 🦀 !!")

    # noinspection PyMethodMayBeStatic
    def test_iter_for_each(self):
        (siter(range(5)).flat_map(lambda x: range(x * 100, x * 110))
         .enumerate()
         .filter(lambda d: (d[0] + d[1]) % 3 == 0)
         .for_each(lambda d: None))

    def test_iter_map(self):
        t = siter(range(10))
        self.assertListEqual(
            t.map(lambda x: x * 2).filter(lambda x: x % 3 == 1).enumerate().collect_list(),
            list(enumerate(filter(lambda x: x % 3 == 1, map(lambda x: x * 2, range(10))))),
        )
        a = [1, 2, 3]
        it = siter(a).map(lambda x: x * 2)
        self.assertEqual(it.next(), Option.some(2))
        self.assertEqual(it.next(), Option.some(4))
        self.assertEqual(it.next(), Option.some(6))
        self.assertEqual(it.next(), Option.none())

        #############
        # Map While #
        #############

        a = [-1, 4, 0, 1]

        it = siter(a).map_while(lambda x: Option.none() if x == 0 else Option.some(16 / x))

        self.assertEqual(it.next(), Option.some(-16))
        self.assertEqual(it.next(), Option.some(4))
        self.assertEqual(it.next(), Option.none())

        a = [-1, 4, 0, 1]

        it = siter(a) \
            .map(lambda x: Option.none() if x == 0 else Option.some(16 / x)) \
            .take_while(lambda x: x.is_some()) \
            .map(lambda x: x.unwrap())

        self.assertEqual(it.next(), Option.some(-16))
        self.assertEqual(it.next(), Option.some(4))
        self.assertEqual(it.next(), Option.none())

        a = [0, 1, 2, -3, 4, 5, -6];

        it = siter(a).map_while(lambda x: Option.none() if x < 0 else Option.some(x))
        lst = it.collect_list()

        self.assertListEqual(lst, [0, 1, 2])

        a = [1, 2, -3, 4]
        it = siter(a)

        res = it.map_while(lambda x: Option.none() if x < 0 else Option.some(x)).collect_list()

        self.assertListEqual(res, [1, 2])

        res2 = it.collect_list()

        self.assertListEqual(res2, [4])

        ###############
        # Map Windows #
        ###############

        strings = siter('abcd') \
            .map_windows(2, lambda dq: f'{dq[0]}+{dq[1]}') \
            .collect_list()

        self.assertListEqual(strings, ["a+b", "b+c", "c+d"])

        limited = siter("abcd").map_windows(5, lambda dq: dq)
        self.assertEqual(limited.next(), Option.none())
        self.assertEqual(limited.next(), Option.none())

    def test_iter_peek(self):
        xs = [1, 2, 3]
        it = siter(xs).peekable()
        self.assertEqual(it.peek(), Option.some(1))
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(it.peek(), Option.some(2))
        self.assertEqual(it.peek(), Option.some(2))
        self.assertEqual(it.next(), Option.some(2))
        self.assertEqual(it.next(), Option.some(3))
        self.assertEqual(it.peek(), Option.none())
        self.assertEqual(it.next(), Option.none())

    def test_iter_fold(self):
        a = [1, 2, 3]
        it = siter(a)
        self.assertEqual(it.fold(0, lambda acc, x: acc + x), 6)

        numbers = [1, 2, 3, 4, 5]
        result = siter(numbers).fold("0", lambda acc, x: f"({acc} + {x})")
        self.assertEqual(result, "(((((0 + 1) + 2) + 3) + 4) + 5)")

    def test_iter_index(self):
        a = [1, 2, 3]
        self.assertEqual(siter(a).find(lambda x: x == 2), Option.some(2))
        self.assertEqual(siter(a).find(lambda x: x == 5), Option.none())

        a = ["lol", "wow", "2", "5"]
        res = siter(a).find_map(lambda x: Result.catch_from(int, x).ok())
        self.assertEqual(res, Option.some(2))

        a = [1, 2, 3]

        self.assertTrue(siter(a).exist(2))
        self.assertFalse(siter(a).exist(5))

        self.assertEqual(siter(a).position(lambda x: x == 2), Option.some(1))
        self.assertEqual(siter(a).position(lambda x: x == 5), Option.none())

        self.assertEqual(siter(a).index(2), Option.some(1))
        self.assertEqual(siter(a).index(5), Option.none())

    def test_iter_reduce(self):
        reduced = siter(range(10)).reduce(lambda acc, e: acc + e)
        self.assertEqual(reduced, Option.some(45))
        self.assertEqual(reduced.unwrap(), siter(range(10)).fold(0, lambda acc, e: acc + e))

        a = [1, 2, 3]
        self.assertEqual(siter(a).sum(), Option.some(6))

        self.assertEqual(siter(range(1, 6)).product(), Option.some(120))
        self.assertEqual(siter(range(1, 1)).product(), Option.none())

    def test_iter_scan(self):
        a = [1, 2, 3, 4]

        def scanner(state: int, x: int):
            st = state * x
            if st > 6:
                res = Option.none()
            else:
                res = Option.some(-st)
            return st, res

        it = siter(a).scan(1, scanner)

        self.assertEqual(it.next(), Option.some(-1))
        self.assertEqual(it.next(), Option.some(-2))
        self.assertEqual(it.next(), Option.some(-6))
        self.assertEqual(it.next(), Option.none())

    def test_iter_skip(self):
        a = [1, 2, 3]
        it = siter(a).skip(2)
        self.assertEqual(it.next(), Option.some(3))
        self.assertEqual(it.next(), Option.none())
        self.assertEqual(it.next(), Option.none())

    def test_iter_take(self):
        a = [1, 2, 3]
        it = siter(a).take(2)
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(it.next(), Option.some(2))
        self.assertEqual(it.next(), Option.none())

        def fib():
            _f1 = 1
            _f2 = 1
            yield _f1
            yield _f2
            while True:
                _f3 = _f1 + _f2
                yield _f3
                _f1 = _f2
                _f2 = _f3

        it = siter(fib()).take(4)
        self.assertListEqual(it.collect_list(), [1, 1, 2, 3])
        it = siter(fib()).skip(5).take(5)
        self.assertListEqual(it.collect_list(), [8, 13, 21, 34, 55])

        a = [-1, 0, 1]
        it = siter(a).take_while(lambda v: v < 0)
        self.assertEqual(it.next(), Option.some(-1))
        self.assertEqual(it.next(), Option.none())

        a = [-1, 0, 1, -2]
        it = siter(a).take_while(lambda v: v < 0)
        self.assertEqual(it.next(), Option.some(-1))
        self.assertEqual(it.next(), Option.none())
        self.assertEqual(it.next(), Option.none())
        self.assertEqual(it.next(), Option.none())

        a = [1, 2, 3, 4]
        it = siter(a)
        result = it.take_while(lambda v: v != 3).collect_list()
        self.assertListEqual(result, [1, 2])
        result = it.collect_list()
        self.assertListEqual(result, [4])

    def test_iter_zip(self):
        a1 = [1, 3, 5]
        a2 = [2, 4, 6]
        it = siter(a1).zip(siter(a2))
        self.assertEqual(it.next(), Option.some((1, 2)))
        self.assertEqual(it.next(), Option.some((3, 4)))
        self.assertEqual(it.next(), Option.some((5, 6)))
        self.assertEqual(it.next(), Option.none())

    def test_iter_chain(self):
        element = 1
        it = once(element)
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(it.next(), Option.none())

        a1 = [1, 3, 5]
        a2 = [2, 4, 6]
        it1 = siter(a1)
        it2 = siter(a2)
        self.assertListEqual(it1.chain(it2).collect_list(), [1, 3, 5, 2, 4, 6])

    def test_iter_once(self):
        it = once(1)
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(it.next(), Option.none())

        flag = 0

        def closure() -> int:
            nonlocal flag
            flag += 1
            return flag

        it = once_with(closure)
        self.assertEqual(flag, 0)
        self.assertEqual(it.next(), Option.some(1))
        self.assertEqual(flag, 1)
        self.assertEqual(it.next(), Option.none())
        self.assertEqual(flag, 1)

        it = once_with(lambda: 1)
        self.assertEqual(it.advance_by(0), Ok(None))
        self.assertEqual(it.advance_by(1), Ok(None))
        self.assertEqual(it.advance_by(100), Err(100))
        it = once_with(lambda: 1)
        self.assertEqual(it.advance_by(100), Err(99))

        it = once_with(lambda: 1)
        self.assertEqual(it.next_chunk(1), Ok([1]))
        self.assertEqual(it.next_chunk(1), Err([]))
        it = once_with(lambda: 1)
        self.assertEqual(it.next_chunk(2), Err([1]))

        it = once_with(lambda: 1)
        self.assertEqual(it.nth(0), Option.some(1))
        self.assertEqual(it.nth(0), Option.none())
        it = once_with(lambda: 1)
        self.assertEqual(it.nth(1), Option.none())

    def test_iter_repeat(self):
        it = repeat(5)
        self.assertListEqual(it.take(5).collect_list(), [5] * 5)

    def test_iter_chunk(self):
        a = siter("loerm").array_chunk(2)
        self.assertEqual(a.next(), Option.some(["l", "o"]))
        self.assertEqual(a.next(), Option.some(["e", "r"]))
        self.assertEqual(a.next(), Option.none())
        self.assertListEqual(a.get_unused().unwrap(), ["m"])
        self.assertListEqual(a.get_unused().unwrap(), ["m"])

        it = siter([1, 2, 3, 4]).array_chunk(3)
        self.assertEqual(it.next(), Option.some([1, 2, 3]))
        self.assertEqual(it.next(), Option.none())
        self.assertEqual(it.get_unused(), Option.some([4]))

        a = siter("loerm").chunk(2)
        self.assertEqual(a.next(), Option.some(["l", "o"]))
        self.assertEqual(a.next(), Option.some(["e", "r"]))
        self.assertEqual(a.next(), Option.some(["m"]))
        self.assertIsNone(a.next().to_nullable())

    def test_iter_check(self):
        a = [1, 2, 3]
        self.assertTrue(siter(a).all(lambda x: x > 0))
        self.assertFalse(siter(a).all(lambda x: x > 2))
        a = [1, 2, 3]
        it = siter(a)
        self.assertFalse(it.all(lambda x: x != 2))
        self.assertEqual(it.next(), Option.some(3))

        a = [1, 2, 3]
        self.assertTrue(siter(a).any(lambda x: x > 2))
        self.assertFalse(siter(a).any(lambda x: x > 5))
        a = [1, 2, 3]
        it = siter(a)
        self.assertTrue(it.any(lambda x: x != 2))
        self.assertEqual(it.next(), Option.some(2))

    def test_max_min(self):
        a = [1, 3, 2]

        m = siter(a).max()
        self.assertEqual(m, Option.some(3))

        a = [element.Element(0, 0), element.Element(3, 1), element.Element(2, 2), element.Element(3, 3)]

        m = siter(a).max()
        self.assertTrue(m.unwrap().same_as(element.Element(3, 3)))

        a = [-3, 0, 1, 5, -10]
        self.assertEqual(siter(a).max_by(lambda x, y: mutils.cmp.compare(y, x)), Option.some(-10))

        lst = [element.Element(0, 0), element.Element(5, 1), element.Element(2, 2)]
        m = siter(lst).max_by_key(lambda el: el.value)
        self.assertTrue(m.unwrap().same_as(element.Element(5, 1)))

        a = [1, 3, 2]

        m = siter(a).min()
        self.assertEqual(m, Option.some(1))

        a = [element.Element(0, 0), element.Element(3, 1), element.Element(2, 2), element.Element(0, 3)]

        m = siter(a).min()
        self.assertTrue(m.unwrap().same_as(element.Element(0, 3)))

        a = [-3, 0, 1, 5, -10]
        self.assertEqual(siter(a).min_by(lambda x, y: mutils.cmp.compare(y, x)), Option.some(5))

        lst = [element.Element(0, 0), element.Element(5, 1), element.Element(2, 2)]
        m = siter(lst).min_by_key(lambda el: el.value)
        self.assertTrue(m.unwrap().same_as(element.Element(0, 0)))

    def test_partition(self):
        a = [0, 1, 2, 3, 4]
        left = []
        right = []
        siter(a).partition(lambda item: item % 2 == 0, left, right)
        self.assertListEqual(left, [0, 2, 4])
        self.assertListEqual(right, [1, 3])

        left, right = siter(a).partition_list(lambda item: item % 2 == 0)
        self.assertListEqual(left, [0, 2, 4])
        self.assertListEqual(right, [1, 3])

    def test_batch(self):
        def do_batch(it) -> Option[t.Tuple[int, int]]:
            nxt = it.next()
            if nxt.is_none():
                return Option.none()
            else:
                nxt2 = it.next()
                if nxt2.is_none():
                    return Option.none()
                else:
                    return Option.some((nxt.unwrap_unchecked(), nxt2.unwrap_unchecked()))

        pit = siter(range(0, 4)).batching(do_batch)

        self.assertListEqual(pit.collect_list(), [(0, 1), (2, 3)])


if __name__ == "__main__":
    unittest.main()
