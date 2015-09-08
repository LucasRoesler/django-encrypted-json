# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_encrypted_json.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TestModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('json', django_encrypted_json.fields.EncryptedValueJsonField(default={})),
                ('optional_json', django_encrypted_json.fields.EncryptedValueJsonField(null=True, blank=True)),
            ],
        ),
    ]
