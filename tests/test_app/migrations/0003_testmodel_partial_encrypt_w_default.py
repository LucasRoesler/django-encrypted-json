# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_encrypted_json.fields


class Migration(migrations.Migration):

    dependencies = [
        ('test_app', '0002_testmodel_partial_encrypt'),
    ]

    operations = [
        migrations.AddField(
            model_name='testmodel',
            name='partial_encrypt_w_default',
            field=django_encrypted_json.fields.EncryptedValueJsonField(default=[], blank=True),
        ),
    ]
