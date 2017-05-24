# -*- coding: utf-8 -*-
import os, sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/../libs')
import helpers
from modules.enumerate_peek import enumerate_peek

class EnumeratePeekTest(unittest.TestCase):

    def test_should_return_empty_iterator_given_empty_iterator(self):
        mock_generator = iter(())
        was_called = False
        for x, has_next in enumerate_peek(mock_generator):
            was_called = True
        self.assertFalse(was_called, "Expected no enumeration of empty iterator")

    def test_has_next_should_return_true_given_more_items_exist(self):
        mock_generator = iter(range(2))
        x, has_next = next(enumerate_peek(mock_generator))
        self.assertTrue(has_next)

    def test_has_next_should_return_false_given_no_more_items_exist(self):
        mock_generator = iter(range(1))
        x, has_next = next(enumerate_peek(mock_generator))
        self.assertFalse(has_next)

    def test_should_iterate_over_all_items_given_iterator(self):
        mock_generator = iter(range(3))
        call_count = 0
        for x, has_next in enumerate_peek(mock_generator):
            call_count += 1
        self.assertEqual(call_count, 3)

    def test_should_iterate_over_all_items_given_list(self):
        my_list = [1,2,3]
        call_count = 0
        for x, has_next in enumerate_peek(my_list):
            call_count += 1
        self.assertEqual(call_count, 3)

if __name__ == '__main__':
    unittest.main(verbosity=2)
