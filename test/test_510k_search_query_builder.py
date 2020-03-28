#!/usr/bin/env python
"""
Unit tests for SearchQueryBuilder510k
"""

import unittest

from src import fda_510k_api

class TestSearchQueryBuilder(unittest.TestCase):
    def test_init(self):
        builder = fda_510k_api.SearchQueryBuilder510k()
        expected_query_str = fda_510k_api.EMPTY_STR
        self.assertEqual(expected_query_str, builder.query_string)
        self.assertFalse(builder.has_query_field)

    def test_add_first_query_field(self):
        builder = fda_510k_api.SearchQueryBuilder510k()

        # Add the first query field
        field_name = "field_name_1"
        field_value = "field_value_1"
        builder.add_first_query_field(field_name, field_value)

        expected_query_str = field_name + fda_510k_api.QUERY_FIELD_COLON + field_value

        self.assertEqual(expected_query_str, builder.get_search_query_string())


    # Add a query field using logical OR
    def test_add_query_field_or(self):
        builder = fda_510k_api.SearchQueryBuilder510k()

        # Add the first query field
        first_field_name = "field_name_1"
        first_field_value = "field_value_1"
        builder.add_first_query_field(first_field_name, first_field_value)

        # Add the second query field with logical OR
        second_field_name = "second_field_name"
        second_field_value = "second_field_value"
        builder.add_query_field(second_field_name, second_field_value, fda_510k_api.LOGICAL_OR_510k)

        expected_query_str = first_field_name + fda_510k_api.QUERY_FIELD_COLON + first_field_value + \
        fda_510k_api.LOGICAL_OR_510k + second_field_name + fda_510k_api.QUERY_FIELD_COLON + second_field_value

        self.assertEqual(expected_query_str, builder.get_search_query_string())

    # Add a query field that has an invalid logical operator
    def test_add_query_field_invalid(self):
        builder = fda_510k_api.SearchQueryBuilder510k()

        # Add the first query field
        first_field_name = "field_name_1"
        first_field_value = "field_value_1"
        builder.add_first_query_field(first_field_name, first_field_value)

        # Add the second query field with an invalid logical operator
        second_field_name = "second_field_name"
        second_field_value = "second_field_value"
        invalid_logical_operator = "INVALID"

        with self.assertRaises(ValueError):
            builder.add_query_field(second_field_name, second_field_value, invalid_logical_operator)

if __name__ == '__main__':
    unittest.main()
