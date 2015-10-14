import json

import cryptography.fernet
from django.conf import settings
from django_pgjson.fields import get_encoder_class

# Allow the use of key rotation
if isinstance(settings.FIELD_ENCRYPTION_KEY, (tuple, list)):
    keys = [
        cryptography.fernet.Fernet(k)
        for k in settings.FIELD_ENCRYPTION_KEY
    ]

elif isinstance(settings.FIELD_ENCRYPTION_KEY, dict):
    # allow the keys to be indexed in a dictionary
    keys = [
        cryptography.fernet.Fernet(k)
        for k in settings.FIELD_ENCRYPTION_KEY.values()
    ]
else:
    # else turn the single key into a list of one
    keys = [cryptography.fernet.Fernet(settings.FIELD_ENCRYPTION_KEY), ]

crypter = cryptography.fernet.MultiFernet(keys)


def no_op_encrypt_values(data, encrypter=None, skip_keys=None):
    """
    A noop function with the same call signature of `encrypt_values`.

    Returns:
        obj - returns the data parameter unaltered.
    """
    return data


def pick_encrypter(key, keys, encrypter):
    """
    Returns encrypting function.

    To facilitate skipping keys during encryption we need to pick between the
    encrypting function or a noop funciton.

    Returns:
        function
    """
    if key in keys:
        return no_op_encrypt_values

    return encrypter


def encrypt_values(data, encrypter=None, skip_keys=None):
    """
    Returns data with values it contains recursively encrypted.

    Note that this will use `json.dumps` to convert the data to a string type.
    The encoder class will be the value of `PGJSON_ENCODER_CLASS` in the
    settings or `django.core.serializers.json.DjangoJSONEncoder`.

    Arguments:
        data (object): the data to decrypt.
        encrypter (function): the decryption function to use.  If not
            specified it will use the
            cryptography.fernet.MultiFernetMultiFernet.encrypt method
            with the keys being taken from settings.FIELD_ENCRYPTION_KEY
        skip_keys (list[str]): a list of keys that should not be encrypted

    Returns:
        object
    """
    if skip_keys is None:
        skip_keys = []

    encrypter = encrypter or crypter.encrypt

    if isinstance(data, (list, tuple, set)):
        return [encrypt_values(x, encrypter, skip_keys) for x in data]

    if isinstance(data, dict):

        return {
            key: pick_encrypter(key, skip_keys, encrypt_values)(
                value, encrypter, skip_keys)
            for key, value in data.iteritems()
        }

    if isinstance(data, basestring):
        return encrypter(data.encode('unicode_escape'))

    return encrypter(
        bytes(json.dumps(data, cls=get_encoder_class()))
    )


def decrypt_values(data, decrypter=None):
    """
    Returns data with values it contains recursively decrypted.

    Note that this will use `json.loads` to convert the decrypted data to
    its most likely python type.

    Arguments:
        data (object): the data to decrypt.
        decrypter (function): the decryption function to use.  If not
            specified it will use the
            cryptography.fernet.MultiFernetMultiFernet.decrypt method
            with the keys being taken from settings.FIELD_ENCRYPTION_KEY

    Returns:
        object
    """
    decrypter = decrypter or crypter.decrypt

    if isinstance(data, (list, tuple, set)):
        return [decrypt_values(x, decrypter) for x in data]

    if isinstance(data, dict):
        return {
            key: decrypt_values(value, decrypter)
            for key, value in data.iteritems()
        }

    if isinstance(data, basestring):
        # string data! if we got a string or unicode convert it to
        # bytes first, as per http://stackoverflow.com/a/11174804.
        #
        # Note 1: This is required for the decrypter, it only accepts bytes.
        # Note 2: this is primarily needed because the decrypt method is called
        # on the value during the save as well as during the read, by the
        # django ORM.
        data = data.encode('unicode_escape')

    try:
        # decrypt the bytes data
        value = decrypter(data)
    except TypeError:
        # Not bytes data??! probably from a django field calling
        # to_python during value assignment
        value = data
    except cryptography.fernet.InvalidToken:
        # Either the data is corrupted, e.g. a lost key or the data
        # was never encrypted, this could be from django calling to_python
        # during value assignment.
        value = data

    try:
        # undo the unicode mess from earlier
        value = value.decode('unicode_escape')
    except AttributeError:
        pass

    try:
        return json.loads(value)
    except (ValueError, TypeError):
        # Not valid json, just return the value
        return value
