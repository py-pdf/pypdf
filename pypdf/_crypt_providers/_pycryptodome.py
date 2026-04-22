# Copyright (c) 2023, exiledkingcc
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# * The name of the author may not be used to endorse or promote products
# derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import secrets

from Crypto import __version__
from Crypto.Cipher import AES, ARC4
from Crypto.Util.Padding import pad, unpad

from pypdf._crypt_providers._base import CryptBase
from pypdf._utils import logger_warning
from pypdf.errors import PdfStreamError

crypt_provider = ("pycryptodome", __version__)


class CryptRC4(CryptBase):
    def __init__(self, key: bytes) -> None:
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        return ARC4.ARC4Cipher(self.key).encrypt(data)

    def decrypt(self, data: bytes, *, strict: bool = True) -> bytes:
        return ARC4.ARC4Cipher(self.key).decrypt(data)


class CryptAES(CryptBase):
    def __init__(self, key: bytes) -> None:
        self.key = key

    def encrypt(self, data: bytes) -> bytes:
        iv = secrets.token_bytes(16)
        padded_data = pad(data, 16)
        aes = AES.new(self.key, AES.MODE_CBC, iv)
        return iv + aes.encrypt(padded_data)

    def decrypt(self, data: bytes, *, strict: bool = True) -> bytes:
        iv = data[:16]
        data = data[16:]
        # for empty encrypted data
        if not data:
            return data

        aes = AES.new(self.key, AES.MODE_CBC, iv)
        padded_data = aes.decrypt(data)
        try:
            return unpad(padded_data, 16)
        except ValueError as exception:
            if strict:
                raise PdfStreamError(exception)
            logger_warning("Ignoring padding error: %s", __name__, exception=exception)
            return padded_data[: -padded_data[-1]]


def rc4_encrypt(key: bytes, data: bytes) -> bytes:
    return ARC4.ARC4Cipher(key).encrypt(data)


def rc4_decrypt(key: bytes, data: bytes) -> bytes:
    return ARC4.ARC4Cipher(key).decrypt(data)


def aes_ecb_encrypt(key: bytes, data: bytes) -> bytes:
    return AES.new(key, AES.MODE_ECB).encrypt(data)


def aes_ecb_decrypt(key: bytes, data: bytes) -> bytes:
    return AES.new(key, AES.MODE_ECB).decrypt(data)


def aes_cbc_encrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).encrypt(data)


def aes_cbc_decrypt(key: bytes, iv: bytes, data: bytes) -> bytes:
    return AES.new(key, AES.MODE_CBC, iv).decrypt(data)
