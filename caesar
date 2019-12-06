def encrypt_caesar(plaintext):
    """
    >>> encrypt_caesar("PYTHON")
    'SBWKRQ'
    >>> encrypt_caesar("python")
    'sbwkrq'
    >>> encrypt_caesar("Python3.6")
    'Sbwkrq3.6'
    >>> encrypt_caesar("")
    ''
    """
    ciphertext = ""

    for letter in plaintext:
        if letter >= "A" and letter <= "Z":
            cryptletter_ord = ord("A")
        elif letter >= "a" and letter <= "z":
            cryptletter_ord = ord("a")
        else:
            ciphertext += letter
            continue

        cryptletter_ord += (ord(letter) - cryptletter_ord + 3) % 26
        ciphertext += chr(cryptletter_ord)

    return ciphertext


def decrypt_caesar(ciphertext):
    """
    >>> decrypt_caesar("SBWKRQ")
    'PYTHON'
    >>> decrypt_caesar("sbwkrq")
    'python'
    >>> decrypt_caesar("Sbwkrq3.6")
    'Python3.6'
    >>> decrypt_caesar("")
    ''
    """
    plaintext = ""

    for cryptLetter in ciphertext:
        if cryptLetter >= "A" and cryptLetter <= "Z":
            encryptletter_ord = ord("Z")
        elif cryptLetter >= "a" and cryptLetter <= "z":
            encryptletter_ord = ord("z")
        else:
            plaintext += cryptLetter
            continue

        encryptletter_ord -= (encryptletter_ord - ord(cryptLetter) + 3) % 26
        plaintext += chr(encryptletter_ord)

    return plaintext
