"""
Asymmetric key encryption object definition.

:author: Max Milazzo
"""


import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from typing import Union


KEY_SIZE = 4096
# asymmetric key size (in bits)


PUBLIC_EXPONENT = 65537
# standard public exponent


class RSA:
    """
    RSA encryption object.
    """

    def __init__(
        self, key_size: int = KEY_SIZE, private_key: Union[bytes, None] = None,
        public_key: Union[bytes, None] = None
    ) -> None:
        """
        RSA encryption object initialization.

        :param key_size: key size (in bits)
        :param public_key: public encryption key to use (if present)
        :param private_key: private decryption key to use (if present)
        """

        if key_size != 1024 and key_size != 2048 and key_size != 4096:
            raise Exception("RSA: invalid key length")
            # raise exception if invalid key size is passed

        if private_key is None and public_key is None:
            self.private_key, self.public_key = self._generate_key_pair(key_size)
            # generate new key pair

        else:
            self.private_key = private_key
            self.public_key = public_key
            # set passed keys
        
        if private_key is not None:
            self._private_key = serialization.load_pem_private_key(
                self.private_key,
                password=None,
                backend=default_backend()
            )
            # initialize private key object for decryption
        
        if public_key is not None:
            self._public_key = serialization.load_pem_public_key(
                self.public_key,
                backend=default_backend()
            )
            # initialize public key object for encryption
        

    def _generate_key_pair(self, key_size: int) -> tuple:
        """
        Generate RSA key pair.

        :param key_size: key size (in bits)
        :return: private and public key pair
        """

        private_key = rsa.generate_private_key(
            public_exponent=PUBLIC_EXPONENT,
            key_size=key_size,
            backend=default_backend()
        )
        # generate new private key

        private_key_bytes = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )
        # encode and format private key bytes

        public_key_bytes = private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        # generate associated public key bytes
        
        return private_key_bytes, public_key_bytes
        

    def encrypt(
        self, plaintext: Union[bytes, str], byte_output: bool = False
    ) -> Union[bytes, str]:
        """
        Perform RSA encryption.

        :param plaintext: plaintext to be encrypted
        :param byte_output: specifies whether to return encrypted data as bytes
            or base64-encoded string

        :return: encrypted data
        """

        if type(plaintext) == str:
            plaintext = plaintext.encode("utf-8")
            # encode plaintext string to bytes

        ciphertext = self._public_key.encrypt(
            plaintext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # encrypt data

        if not byte_output:
            ciphertext = base64.b64encode(ciphertext).decode("utf-8")
            # encode ciphertext as a base64 string

        return ciphertext


    def decrypt(
        self, ciphertext: Union[bytes, str], byte_output: bool = True
    ) -> Union[bytes, str]:
        """
        Perform RSA decryption.

        :param ciphertext: ciphertext to decrypt
        :param byte_output: specifies whether to return decrypted data as bytes
            or decoded UTF-8 string

        :return: decrypted data
        """

        if type(ciphertext) == str:
            ciphertext = base64.b64decode(ciphertext)
            # decode ciphertext base64 string to bytes

        plaintext = self._private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        # decrypt data

        if not byte_output:
            plaintext = base64.b64encode(plaintext).decode("utf-8")
            # decode plaintext as a UTF-8 string

        return plaintext
        
        
AKE = RSA
# standard asymmetric key encryption object (used for key exchange API)