
def generate_temporary_key(public_key1, public_key2, private_key):
    temporary_key = public_key1 ** private_key
    temporary_key = temporary_key % public_key2
    return temporary_key


def generate_symmetric_key(temporary_key, public_key2, private_key):
    symmetric_key = temporary_key ** private_key
    symmetric_key = symmetric_key % public_key2
    return symmetric_key


# It has to be updated, weak encryption
def encrypt_message(message, symmetric_key):
    encrypted_message = ""
    for c in message:
        encrypted_message += chr(ord(c) + symmetric_key)
    return encrypted_message


# Respectively update as above
def decrypt_message(encrypted_message, symmetric_key):
    decrypted_message = ""
    for c in encrypted_message:
        decrypted_message += chr(ord(c) - symmetric_key)
    return decrypted_message
