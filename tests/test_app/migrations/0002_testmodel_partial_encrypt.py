# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_encrypted_json.fields


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='partial_encrypt',
            field=django_encrypted_json.fields.EncryptedValueJsonField(null=True, blank=True),
        ),
    ]
