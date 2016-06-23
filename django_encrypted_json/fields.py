from django.db.models.fields import NOT_PROVIDED
from django_pgjson.fields import JsonField, JsonBField, JsonAdapter

from .utils import decrypt_values, encrypt_values


class EncryptedValueJsonField(JsonField):
    """
    A JSON field that will silently encrypt and decrypt the values of the
    JSON value.  It is based on django-pgjson's JSON field.

    Example:

        {
            'many': [1, 2, 3],
            'many_nested': [{'test': 1}, {'test': 2}],
            'nested_1': {
                'and': u'more',
                'next': 1,
                'previous': 1.0,
                'test': True
            },
            'null': None,
            'test': 1
        }

    will be stored as

        {
            'many': [
                'gAAAAA...',
                'gAAAAA...',
                'gAAAAA...'
            ],
            'many_nested': [
                {'test': 'gAAAAA...'},
                {'test': 'gAAAAA...'}],
            'nested_1': {
                'and': 'gAAAAA...',
                'next': 'gAAAAA...',
                'previous': 'gAAAAA...',
                'test': 'gAAAAA...'
            },
            'null': 'gAAAAA...',
            'test': 'gAAAAA...'
        }

    Note that values will be forced to a string using `json.dumps` and restored
    using `json.loads`.
    """
    def __init__(self, *args, **kwargs):
        self.skip_keys = kwargs.pop('skip_keys', [])

        return super(EncryptedValueJsonField, self).__init__(*args, **kwargs)

    def desconstruct(self):
        name, path, args, kwargs = super(EncryptedValueJsonField, self).deconstruct()
        del kwargs["skip_keys"]
        return name, path, args, kwargs

    def to_python(self, value):
        value = super(EncryptedValueJsonField, self).to_python(value)
        return decrypt_values(value)

    def get_db_prep_value(self, value, connection, prepared=False):
        value = super(JsonField, self).get_db_prep_value(
            value, connection, prepared=prepared
        )

        # Because an empty string is not valid json, replace it with an empty
        # dict
        if self.blank and value == "":
            if self.default != NOT_PROVIDED:
                if callable(self.default):
                    value = self.default()
                else:
                    value = self.default
            else:
                value = {}

        if self.null and value is None:
            return None

        value = encrypt_values(value, skip_keys=self.skip_keys)

        return JsonAdapter(value)


class EncryptedValueJsonBField(JsonBField, EncryptedValueJsonField):
    """
    A JSONB field that will silently encrypt and decrypt the values of the
    JSON value.  It is based on django-pgjson's JSONB field.
    """

    pass
