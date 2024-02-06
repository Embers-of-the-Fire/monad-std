import unittest

from monad_std.prelude import *
from monad_std import UnwrapException


class EitherTest(unittest.TestCase):
    def test_type_checker(self):
        self.assertTrue(Left(5).is_left())
        self.assertFalse(Right(5).is_left())
        self.assertFalse(Left(5).is_right())
        self.assertTrue(Right(5).is_right())

    def test_unwrap(self):
        self.assertEqual(Left(5).unwrap_left(), 5)
        try:
            Right(5).unwrap_left()
        except UnwrapException as e:
            self.assertEqual(str(e), "EitherError: Call `Either.unwrap_left` on a `Right` value.")

        self.assertEqual(Right(5).unwrap_right(), 5)
        try:
            Left(5).unwrap_right()
        except UnwrapException as e:
            self.assertEqual(str(e), "EitherError: Call `Either.unwrap_right` on a `Left` value.")