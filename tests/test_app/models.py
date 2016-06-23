from django.db import models


from django_encrypted_json.fields import EncryptedValueJsonField
# Create your models here.


class TestModel(models.Model):
    json = EncryptedValueJsonField(default={})
    optional_json = EncryptedValueJsonField(blank=True, null=True)
    partial_encrypt = EncryptedValueJsonField(
        blank=True, null=True, skip_keys=('test', ))
    partial_encrypt_w_default = EncryptedValueJsonField(
        blank=True, skip_keys=('test', ), default=[])
