# -*- coding=utf-8 -*-
import datetime
import json

from django.db import connection
from django.test import TestCase
from django.utils import timezone

from .models import TestModel
# Create your tests here.


LATIN1_NON_BREAKING_SPACE = u"""\
~~~New Room Update for Crimson House Should we use this same room for
13:30-14:00 Weekly Sync Meeting (with Gargi)?  Hi All, This is a meeting
call for Rakuten/HCL weekly sync update: to discuss done, on-going and
future tasks. It will also be a place to discuss issues/concerns with
the project.Action points and ownership of tasks (Rakuten or HCL) should
be decided in this part.  https://confluenc
"""

UNICODE_HODGEPODGE = \
    u"Testing «ταБЬℓσ»: 1<2 & 4+1>3, now 20% off! ÄŸÃ¼ÅŸiöçı 木下さん利用"


class PlainJsonField(TestCase):
    maxDiff = 2000

    def test_default_create(self):
        instance = TestModel.objects.create()

        self.assertEquals(instance.json, {})
        self.assertEquals(instance.optional_json, None)

    def test_saving_data(self):
        instance = TestModel.objects.create()
        data = {
            'test': 1,
            'null': None,
            'many': [1, 2, 3],
            'nested_1': {
                'test': True,
                'next': 1,
                'previous': 1.0,
                'and': 'more',
                'unicode': u'more'
            },
            'datetime': datetime.datetime.now(),
            'date': datetime.date.today(),
            'with_tz': timezone.now(),
            'many_nested': [{'test': 1}, {'test': 2}]
        }

        instance.json = data
        instance.save()

        cursor = connection.cursor()
        cursor.execute(
            "SELECT json FROM test_app_testmodel WHERE id = %s", [instance.pk]
        )
        row = cursor.fetchone()
        raw_db_data = row[0]

        self.assertIsInstance(raw_db_data, dict)
        self.assertNotEqual(data['test'], raw_db_data['test'])
        self.assertIsInstance(raw_db_data['test'], basestring)
        self.assertIsInstance(raw_db_data['datetime'], basestring)
        self.assertIsInstance(raw_db_data['date'], basestring)
        self.assertIsInstance(raw_db_data['with_tz'], basestring)
        self.assertIsInstance(raw_db_data['many'], list)
        self.assertIsInstance(raw_db_data['nested_1'], dict)
        self.assertIsInstance(raw_db_data['many_nested'], list)

    def test_skipping_keys(self):
        instance = TestModel.objects.create()
        data = {
            'test': 1,
            'null': None,
            'many': [1, 2, 3],
            'nested_1': {
                'test': True,
                'next': 1,
                'previous': 1.0,
                'and': 'more',
                'unicode': u'more'
            },
            'datetime': datetime.datetime.now(),
            'date': datetime.date.today(),
            'with_tz': timezone.now(),
            'many_nested': [{'test': 1}, {'test': 2}]
        }

        instance.partial_encrypt = data
        instance.save()

        cursor = connection.cursor()
        cursor.execute(
            "SELECT partial_encrypt FROM test_app_testmodel WHERE id = %s",
            [instance.pk]
        )
        row = cursor.fetchone()
        raw_db_data = row[0]

        self.assertIsInstance(raw_db_data, dict)
        self.assertEquals(data['test'], raw_db_data['test'])
        self.assertEquals(data['many_nested'], raw_db_data['many_nested'])
        self.assertNotEqual(data['many'], raw_db_data['many'])
        self.assertNotEqual(data['nested_1'], raw_db_data['nested_1'])
        self.assertIsInstance(raw_db_data['datetime'], basestring)
        self.assertIsInstance(raw_db_data['date'], basestring)
        self.assertIsInstance(raw_db_data['with_tz'], basestring)

    def test_latin1(self):
        instance = TestModel.objects.create()
        instance.json = {'test': LATIN1_NON_BREAKING_SPACE}
        instance.save()

        instance.refresh_from_db()
        self.assertEqual(
            instance.json['test'],
            LATIN1_NON_BREAKING_SPACE)

    def test_hodegpodge_unicode(self):
        instance = TestModel.objects.create()
        instance.json = {'test': UNICODE_HODGEPODGE}
        instance.save()

        instance.refresh_from_db()
        self.assertEqual(instance.json['test'], UNICODE_HODGEPODGE)
