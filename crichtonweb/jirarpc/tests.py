# Crichton, Admirable Source Configuration Management
# Copyright 2012 British Broadcasting Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from jirarpc import RemoteJira, IssueBuilder

class RemoteJiraTest(TestCase):
    def test_get_username_from_email_bbc(self):
        """
        get_username_from_email() returns full email address
        """
        self.assertEqual(RemoteJira.get_username_from_email("my.name@domain.local"), "my.name@domain.local")

    def test_get_username_from_email_bbc_funny_chars(self):
        """
        get_username_from_email() works with funny chars like apostrophes
        """
        self.assertEqual(RemoteJira.get_username_from_email("fm&t.o'reilly@domain.local"), "fm&t.o'reilly@domain.local")

    def test_issue_builder_get_issue_create_fields(self):
        """get_issue_create_fields() returns valid dict"""
        ib = IssueBuilder("OPS", "change", test_mode = True)
        fields = ib.get_issue_create_fields()
        self.assertEqual(fields.__class__.__name__, 'dict')
        self.assertEqual(fields['project'], "OPS")

    def _find_field(self, fields, id_name, field_value):
        """Searches an array of dicts with 
        {id_name: field_value, "values": RETURNTHIS}
        If it find an array match it returns the first item only,
        or None if no match at all."""
        for field in fields:
            if field[id_name] == field_value:
                return field['values']
        return None

    def test_issue_builder_get_issue_update_fields(self):
        """get_issue_update_fields() returns valid list"""
        ib = IssueBuilder("OPS", "change", test_mode = True)
        fields = ib.get_issue_update_fields()
        self.assertEqual(fields.__class__.__name__, 'list')
        # Make sure the project field is not present
        self.assertEqual(self._find_field(fields, "id", "project"), None)
        self.assertEqual(self._find_field(fields, "id", "type"), None)

    def test_issue_builder_add_normal_field(self):
        """add_field() adds field in right place"""
        ib = IssueBuilder("OPS", "change", test_mode = True)
        ib.add_field("testname", "testval")

        # When creating, normal fields are "name": "value"
        create_fields = ib.get_issue_create_fields()
        self.assertEqual(create_fields["testname"], "testval")

        # When updating, normal fields are "name": ["value"]
        update_fields = ib.get_issue_update_fields()
        found = self._find_field(update_fields, "id", "testname")
        self.assertTrue(isinstance(found, list))
        self.assertEqual(found[0], "testval")

    def test_issue_builder_add_custom_field(self):
        """add_custom_field() adds field in right place"""
        ib = IssueBuilder("OPS", "change", test_mode = True)
        ib.add_custom_field("testname", "testval", test_mode = True)

        create_fields = ib.get_issue_create_fields()
        found = self._find_field(create_fields["customFieldValues"], "customfieldId", "testname")
        self.assertTrue(isinstance(found, list))
        self.assertEqual(found[0], "testval")

        update_fields = ib.get_issue_update_fields()
        found = self._find_field(update_fields, "id", "testname")
        self.assertTrue(isinstance(found, list))
        self.assertEqual(found[0], "testval")

    def test_issue_builder_add_custom_field_array(self):
        """add_custom_field() doesn't put arrays inside arrays"""
        ib = IssueBuilder("OPS", "change", test_mode = True)
        ib.add_custom_field("testname", ["testval"], test_mode = True)

        create_fields = ib.get_issue_create_fields()
        found = self._find_field(create_fields["customFieldValues"], "customfieldId", "testname")
        self.assertTrue(isinstance(found, list))
        self.assertEqual(found[0], "testval")

        update_fields = ib.get_issue_update_fields()
        found = self._find_field(update_fields, "id", "testname")
        self.assertTrue(isinstance(found, list))
        self.assertEqual(found[0], "testval")

