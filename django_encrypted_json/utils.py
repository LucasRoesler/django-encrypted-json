import json

import cryptography.fernet
from django.conf import settings


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


def encrypt_values(data, encrypter=None):
    """
    Returns data with values it contains recursively encrypted.

    Note that this will use `json.dumps` to convert the data to a string type.

    Arguments:
        data (object): the data to decrypt.
        encrypter (function): the decryption function to use.  If not
            specified it will use the
            cryptography.fernet.MultiFernetMultiFernet.encrypt method
            with the keys being taken from settings.FIELD_ENCRYPTION_KEY

    Returns:
        object
    """
    encrypter = encrypter or crypter.encrypt

    if isinstance(data, (list, tuple, set)):
        return [encrypt_values(x, encrypter) for x in data]

    if isinstance(data, dict):
        return {
            key: encrypt_values(value, encrypter)
            for key, value in data.iteritems()
        }

    return encrypter(bytes(json.dumps(data)))


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

    try:
        # decrypt the bytes data
        value = decrypter(data)
    except TypeError:
        if isinstance(data, basestring):
            # Not bytes data! if we got a string or unicode convert it to
            # bytes first, as per http://stackoverflow.com/a/11174804
            value = decrypter(data.encode('latin-1'))
        else:
            # Not a string type?! probably from a django field calleing
            # to_python while the data is already python
            value = data
    except cryptography.fernet.InvalidToken:
        value = data

    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return value
