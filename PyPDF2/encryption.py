# coding: utf-8
#
# Copyright (c) 2022, exiledkingcc
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

import hashlib
import random
import struct
import typing

from PyPDF2.generic import *


class CryptBase:
    def encrypt(self, data: bytes) -> bytes: return data
    def decrypt(self, data: bytes) -> bytes: return data

try:
    from Crypto.Cipher import ARC4, AES

    class CryptRC4(CryptBase):
        def __init__(self, key: bytes) -> None:
            self.key = key

        def encrypt(self, data: bytes) -> bytes:
            return ARC4.ARC4Cipher(self.key).encrypt(data)

        def decrypt(self, data: bytes) -> bytes:
            return ARC4.ARC4Cipher(self.key).decrypt(data)

    class CryptAES(CryptBase):
        def __init__(self, key: bytes) -> None:
            self.key = key

        def encrypt(self, data: bytes) -> bytes:
            iv = bytes(bytearray(random.randint(0, 255) for _ in range(16)))
            p = 16 - len(data) % 16
            data += bytes(bytearray(p for _ in range(p)))
            aes = AES.new(self.key, AES.MODE_CBC, iv)
            return iv + aes.encrypt(data)

        def decrypt(self, data: bytes) -> bytes:
            iv = data[:16]
            data = data[16:]
            aes = AES.new(self.key, AES.MODE_CBC, iv)
            d = aes.decrypt(data)
            return d[:-d[-1]]

except ImportError:

    from PyPDF2._aes import AESCBC

    class CryptRC4(CryptBase):
        def __init__(self, key: bytes) -> None:
            self.S = list(range(256))
            j = 0
            for i in range(256):
                j = (j + self.S[i] + key[i % len(key)]) % 256
                self.S[i], self.S[j] = self.S[j], self.S[i]

        def encrypt(self, data: bytes) -> bytes:
            S = [x for x in self.S]
            out = list(0 for _ in range(len(data)))
            i, j = 0, 0
            for k in range(len(data)):
                i = (i + 1) % 256
                j = (j + S[i]) % 256
                S[i], S[j] = S[j], S[i]
                x = S[(S[i] + S[j]) % 256]
                out[k] = data[k] ^ x
            return bytes(bytearray(out))

        def decrypt(self, data: bytes) -> bytes:
            return self.encrypt(data)

    class CryptAES(CryptBase):
        def __init__(self, key: bytes) -> None:
            self.aes = AESCBC(key)

        def encrypt(self, data: bytes) -> bytes:
            iv = bytes(bytearray(random.randint(0, 255) for _ in range(16)))
            p = 16 - len(data) % 16
            data += bytes(bytearray(p for _ in range(p)))
            return iv + self.aes.encrypt(iv, data)

        def decrypt(self, data: bytes) -> bytes:
            iv = data[:16]
            data = data[16:]
            d = self.aes.decrypt(iv, data)
            return d[:-d[-1]]


class CryptIdentity(CryptBase):
    pass


_PADDING = bytes([
    0x28, 0xBF, 0x4E, 0x5E, 0x4E, 0x75, 0x8A, 0x41,
    0x64, 0x00, 0x4E, 0x56, 0xFF, 0xFA, 0x01, 0x08,
    0x2E, 0x2E, 0x00, 0xB6, 0xD0, 0x68, 0x3E, 0x80,
    0x2F, 0x0C, 0xA9, 0xFE, 0x64, 0x53, 0x69, 0x7A
])

def _padding(data: bytes) -> bytes:
    return (data + _PADDING)[:32]

def _bytes(text: str) -> bytes:
    try:
        return text.encode('latin-1')
    except Exception:  # noqa
        return text.encode('utf-8')


class StandardSecurityHandler:
    def __init__(self, rev: int, perm: int, keylen: int, metadata_encrypted: bool, first_id_entry: bytes) -> None:
        self.R = rev
        self.P = (perm + 0x100000000) % 0x100000000  # maybe < 0
        self.Length = keylen
        self.metadata_encrypted = metadata_encrypted
        self.id1_entry = first_id_entry if first_id_entry is not None else b""

        self.key: typing.Optional[bytes] = None

    def generate(self, user_pwd: str, owner_pwd: str=None) -> typing.Tuple[bytes, bytes]:
        u_entry = self._compute_U_value(user_pwd, owner_pwd)
        o_entry = self._compute_O_value(user_pwd, owner_pwd)
        return u_entry, o_entry

    def auth(self, u_entry: bytes, o_entry: bytes, user_pwd: str, owner_pwd: str=None) -> int:
        if self._auth_user_password(u_entry, o_entry, user_pwd):
            return 1
        elif self._auth_owner_password(u_entry, o_entry, owner_pwd):
            return 2
        else:
            self.key = None
            return 0

    def _compute_key(self, password: bytes, o_entry: bytes) -> bytes:
        """
        Algorithm 2: Computing an encryption key
        """

        """ a) Pad or truncate the password string to exactly 32 bytes. If the password string is more than 32 bytes long,
               use only its first 32 bytes; if it is less than 32 bytes long, pad it by appending the required number of
               additional bytes from the beginning of the following padding string:
                   < 28 BF 4E 5E 4E 75 8A 41 64 00 4E 56 FF FA 01 08
                   2E 2E 00 B6 D0 68 3E 80 2F 0C A9 FE 64 53 69 7A >
               That is, if the password string is n bytes long, append the first 32 - n bytes of the padding string to the end
               of the password string. If the password string is empty (zero-length), meaning there is no user password,
               substitute the entire padding string in its place.
        """
        a = _padding(password)
        """ b) Initialize the MD5 hash function and pass the result of step (a) as input to this function. """
        u_hash = hashlib.md5(a)
        """ c) Pass the value of the encryption dictionary’s O entry to the MD5 hash function. ("Algorithm 3: Computing
               the encryption dictionary’s O (owner password) value" shows how the O value is computed.)
        """
        u_hash.update(o_entry)
        """ d) Convert the integer value of the P entry to a 32-bit unsigned binary number and pass these bytes to the
               MD5 hash function, low-order byte first.
        """
        u_hash.update(struct.pack('<I', self.P))
        """ e) Pass the first element of the file’s file identifier array (the value of the ID entry in the document’s trailer
               dictionary; see Table 15) to the MD5 hash function.
        """
        u_hash.update(self.id1_entry)
        """ f) (Security handlers of revision 4 or greater) If document metadata is not being encrypted, pass 4 bytes with
               the value 0xFFFFFFFF to the MD5 hash function.
        """
        if self.R >= 3 and not self.metadata_encrypted:
            u_hash.update(b"\xff\xff\xff\xff")
        """ g) Finish the hash. """
        u_hash_digest = u_hash.digest()
        """ h) (Security handlers of revision 3 or greater) Do the following 50 times: Take the output from the previous
               MD5 hash and pass the first n bytes of the output as input into a new MD5 hash, where n is the number of
               bytes of the encryption key as defined by the value of the encryption dictionary’s Length entry.
        """
        length = self.Length // 8
        if self.R >= 3:
            for _ in range(50):
                u_hash_digest = hashlib.md5(u_hash_digest[:length]).digest()
        """ i) Set the encryption key to the first n bytes of the output from the final MD5 hash, where n shall always be 5
               for security handlers of revision 2 but, for security handlers of revision 3 or greater, shall depend on the
               value of the encryption dictionary’s Length entry.
        """
        return u_hash_digest[:length]

    def _compute_O_value(self, user_pwd: bytes, owner_pwd: bytes=None) -> bytes:
        """
        Algorithm 3: Computing the encryption dictionary’s O (owner password) value
        """

        """ a) Pad or truncate the owner password string as described in step (a) of "Algorithm 2: Computing an
               encryption key". If there is no owner password, use the user password instead.
        """
        a = _padding(owner_pwd if owner_pwd else user_pwd)
        """ b) Initialize the MD5 hash function and pass the result of step (a) as input to this function. """
        o_hash_digest = hashlib.md5(a).digest()
        """ c) (Security handlers of revision 3 or greater) Do the following 50 times: Take the output from the previous
               MD5 hash and pass it as input into a new MD5 hash. """
        if self.R >= 3:
            for _ in range(50):
                o_hash_digest = hashlib.md5(o_hash_digest).digest()
        """ d) Create an RC4 encryption key using the first n bytes of the output from the final MD5 hash, where n shall
               always be 5 for security handlers of revision 2 but, for security handlers of revision 3 or greater, shall
               depend on the value of the encryption dictionary’s Length entry.
        """
        rc4_key = o_hash_digest[:self.Length // 8]
        """ e) Pad or truncate the user password string as described in step (a) of "Algorithm 2: Computing an encryption key". """
        a = _padding(user_pwd)
        """ f) Encrypt the result of step (e), using an RC4 encryption function with the encryption key obtained in step (d). """
        rc4_enc = CryptRC4(rc4_key).encrypt(a)
        """ g) (Security handlers of revision 3 or greater) Do the following 19 times: Take the output from the previous
               invocation of the RC4 function and pass it as input to a new invocation of the function; use an encryption
               key generated by taking each byte of the encryption key obtained in step (d) and performing an XOR
               (exclusive or) operation between that byte and the single-byte value of the iteration counter (from 1 to 19).
        """
        if self.R >= 3:
            for i in range(1, 20):
                key = bytes(bytearray([x ^ i for x in rc4_key]))
                rc4_enc = CryptRC4(key).encrypt(rc4_enc)
        """ h) Store the output from the final invocation of the RC4 function as the value of the O entry in the encryption dictionary. """
        return rc4_enc

    def _compute_U_value(self, user_pwd: bytes, o_entry: bytes) -> bytes:
        """
        Algorithm 4: Computing the encryption dictionary’s U (user password) value (Security handlers of revision 2)
        """
        """ a) Create an encryption key based on the user password string, as described in "Algorithm 2: Computing an encryption key". """
        self.key = self._compute_key(user_pwd, o_entry)
        """ b) Encrypt the 32-byte padding string shown in step (a) of "Algorithm 2: Computing an encryption key", using
               an RC4 encryption function with the encryption key from the preceding step.
            c) Store the result of step (b) as the value of the U entry in the encryption dictionary.
        """
        if self.R <= 2:
            value = CryptRC4(self.key).encrypt(_PADDING)
            return value

        """
        Algorithm 5: Computing the encryption dictionary’s U (user password) value (Security handlers of revision 3 or greater)
        """
        """ a) Create an encryption key based on the user password string, as described in "Algorithm 2: Computing an encryption key". """
        """ b) Initialize the MD5 hash function and pass the 32-byte padding string shown in step (a) of "Algorithm 2:
               Computing an encryption key" as input to this function. """
        u_hash = hashlib.md5(_PADDING)
        """ c) Pass the first element of the file’s file identifier array (the value of the ID entry in the document’s trailer
               dictionary; see Table 15) to the hash function and finish the hash. """
        u_hash.update(self.id1_entry)
        """ d) Encrypt the 16-byte result of the hash, using an RC4 encryption function with the encryption key from step (a). """
        rc4_enc = CryptRC4(self.key).encrypt(u_hash.digest())
        """ e) Do the following 19 times: Take the output from the previous invocation of the RC4 function and pass it as
               input to a new invocation of the function; use an encryption key generated by taking each byte of the
               original encryption key obtained in step (a) and performing an XOR (exclusive or) operation between that
               byte and the single-byte value of the iteration counter (from 1 to 19).
        """
        for i in range(1, 20):
            key = bytes(bytearray([x ^ i for x in self.key]))
            rc4_enc = CryptRC4(key).encrypt(rc4_enc)
        """ f) Append 16 bytes of arbitrary padding to the output from the final invocation of the RC4 function and store
               the 32-byte result as the value of the U entry in the encryption dictionary.
        """
        return _padding(rc4_enc)

    def _auth_user_password(self, u_entry: bytes, o_entry: bytes, user_pwd: bytes) -> bool:
        """
        Algorithm 6: Authenticating the user password

        a) Perform all but the last step of "Algorithm 4: Computing the encryption dictionary’s U (user password)
           value (Security handlers of revision 2)" or "Algorithm 5: Computing the encryption dictionary’s U (user
           password) value (Security handlers of revision 3 or greater)" using the supplied password string.
        b) If the result of step (a) is equal to the value of the encryption dictionary’s U entry (comparing on the first 16
           bytes in the case of security handlers of revision 3 or greater), the password supplied is the correct user
           password. The key obtained in step (a) (that is, in the first step of "Algorithm 4: Computing the encryption
           dictionary’s U (user password) value (Security handlers of revision 2)" or "Algorithm 5: Computing the
           encryption dictionary’s U (user password) value (Security handlers of revision 3 or greater)") shall be used
           to decrypt the document.
        """
        u_value = self._compute_U_value(user_pwd, o_entry)
        if self.R >= 3:
            u_value = u_value[:16]
            u_entry = u_entry[:16]
        return u_value == u_entry

    def _auth_owner_password(self, u_entry: bytes, o_entry: bytes, owner_pwd: bytes=None) -> bool:
        """
        Algorithm 7: Authenticating the owner password

        a) Compute an encryption key from the supplied password string, as described in steps (a) to (d) of
           "Algorithm 3: Computing the encryption dictionary’s O (owner password) value".
        b) (Security handlers of revision 2 only) Decrypt the value of the encryption dictionary’s O entry, using an RC4
           encryption function with the encryption key computed in step (a).
           (Security handlers of revision 3 or greater) Do the following 20 times: Decrypt the value of the encryption
           dictionary’s O entry (first iteration) or the output from the previous iteration (all subsequent iterations),
           using an RC4 encryption function with a different encryption key at each iteration. The key shall be
           generated by taking the original key (obtained in step (a)) and performing an XOR (exclusive or) operation
           between each byte of the key and the single-byte value of the iteration counter (from 19 to 0).
        c) The result of step (b) purports to be the user password. Authenticate this user password using "Algorithm 6:
           Authenticating the user password". If it is correct, the password supplied is the correct owner password.
        """
        if owner_pwd is None:
            owner_pwd = b""
        a = _padding(owner_pwd)
        o_hash_digest = hashlib.md5(a).digest()
        if self.R >= 3:
            for _ in range(50):
                o_hash_digest = hashlib.md5(o_hash_digest).digest()
        rc4_key = o_hash_digest[:self.Length // 8]

        if self.R <= 2:
            u_pwd = CryptRC4(rc4_key).decrypt(o_entry)
        else:
            u_pwd = o_entry
            for i in range(19, -1, -1):
                key = bytes(bytearray([x ^ i for x in rc4_key]))
                u_pwd = CryptRC4(key).decrypt(u_pwd)
        return self._auth_user_password(u_entry, o_entry, u_pwd)


class CryptFilter:
    def __init__(self, stmCrypt: CryptBase, strCrypt: CryptBase, efCrypt: CryptBase) -> None:
        self.stmCrypt = stmCrypt
        self.strCrypt = strCrypt
        self.efCrypt = efCrypt

    def encryptObject(self, obj: PdfObject) -> PdfObject:
        # TODO
        return NotImplemented

    def decryptObject(self, obj: PdfObject) -> PdfObject:
        if isinstance(obj, ByteStringObject) or isinstance(obj, TextStringObject):
            data = self.strCrypt.decrypt(obj.original_bytes)
            obj = createStringObject(data)
        elif isinstance(obj, StreamObject):
            obj._data = self.stmCrypt.decrypt(obj._data)
        elif isinstance(obj, DictionaryObject):
            for dictkey, value in list(obj.items()):
                obj[dictkey] = self.decryptObject(value)
        elif isinstance(obj, ArrayObject):
            for i in range(len(obj)):
                obj[i] = self.decryptObject(obj[i])
        return obj


class Encryption:
    def __init__(self, algV: int, rev: int, perm: int, keylen: int,
                metadata_encrypted: bool, first_id_entry: bytes,
                StmF: str, StrF: str, EFF: str) -> None:
        self.algV = algV
        self.handler = StandardSecurityHandler(rev, perm, keylen, metadata_encrypted, first_id_entry)
        self.StmF = StmF
        self.StrF = StrF
        self.EFF = EFF

    def key(self) -> typing.Optional[bytes]:
        return self.handler.key

    def encryptObject(self, obj: PdfObject) -> PdfObject:
        # TODO
        return NotImplemented

    def decryptObject(self, obj: PdfObject, idnum: int, generation: int) -> PdfObject:
        """
        Algorithm 1: Encryption of data using the RC4 or AES algorithms

        a) Obtain the object number and generation number from the object identifier of the string or stream to be
           encrypted (see 7.3.10, "Indirect Objects"). If the string is a direct object, use the identifier of the indirect
           object containing it.
        b) For all strings and streams without crypt filter specifier; treating the object number and generation number
           as binary integers, extend the original n-byte encryption key to n + 5 bytes by appending the low-order 3
           bytes of the object number and the low-order 2 bytes of the generation number in that order, low-order byte
           first. (n is 5 unless the value of V in the encryption dictionary is greater than 1, in which case n is the value
           of Length divided by 8.)
           If using the AES algorithm, extend the encryption key an additional 4 bytes by adding the value “sAlT”,
           which corresponds to the hexadecimal values 0x73, 0x41, 0x6C, 0x54. (This addition is done for backward
           compatibility and is not intended to provide additional security.)
        c) Initialize the MD5 hash function and pass the result of step (b) as input to this function.
        d) Use the first (n + 5) bytes, up to a maximum of 16, of the output from the MD5 hash as the key for the RC4
           or AES symmetric key algorithms, along with the string or stream data to be encrypted.
           If using the AES algorithm, the Cipher Block Chaining (CBC) mode, which requires an initialization vector,
           is used. The block size parameter is set to 16 bytes, and the initialization vector is a 16-byte random
           number that is stored as the first 16 bytes of the encrypted stream or string.
        """
        pack1 = struct.pack("<i", idnum)[:3]
        pack2 = struct.pack("<i", generation)[:2]

        key = self.handler.key
        keylen = self.handler.Length
        n = 5 if self.algV == 1 else keylen // 8
        key_data = key[:n] + pack1 + pack2
        key_hash = hashlib.md5(key_data)
        rc4_key = key_hash.digest()[:min(n + 5, 16)]
        #
        key_hash.update(b"sAlT")
        aes_key = key_hash.digest()[:min(n + 5, 16)]

        stmCrypt = self._getCrypt(self.StmF, rc4_key, aes_key)
        StrCrypt = self._getCrypt(self.StrF, rc4_key, aes_key)
        efCrypt = self._getCrypt(self.EFF, rc4_key, aes_key)

        cf = CryptFilter(stmCrypt, StrCrypt, efCrypt)
        return cf.decryptObject(obj)

    @staticmethod
    def _getCrypt(method: str, rc4_key: bytes, aes_key: bytes) -> CryptBase:
        if method == "/AESV2":
            return CryptAES(aes_key)
        elif method == "/Identity":
            return CryptIdentity()
        else:
            return CryptRC4(rc4_key)

    def encryptPdf(self, user_pwd: str, owner_pwd: str=None) -> DictionaryObject:
        # TODO
        return NotImplemented

    def decryptPdf(self, u_entry: bytes, o_entry: bytes, user_pwd: str, owner_pwd: str=None) -> int:
        user_pwd = _bytes(user_pwd)
        if owner_pwd is not None:
            owner_pwd = _bytes(owner_pwd)
        return self.handler.auth(u_entry, o_entry, user_pwd, owner_pwd)

    @staticmethod
    def read(encryption_entry: DictionaryObject, first_id_entry: bytes=None) -> "Encryption":
        filter = encryption_entry.get("/Filter")
        if filter != "/Standard":
            raise NotImplementedError("only Standard PDF encryption handler is available")
        if "/SubFilter" in encryption_entry:
            raise NotImplementedError("/SubFilter NOT supported")

        StmF = "/V2"
        StrF = "/V2"
        EFF = "/V2"

        V = encryption_entry.get("/V", 0)
        if V not in (1, 2, 3, 4):
            raise NotImplementedError("Encryption V=%d NOT supported" % V)
        if V == 4:
            filters = encryption_entry["/CF"]

            StmF = encryption_entry.get("/StmF", "/Identity")
            StrF = encryption_entry.get("/StrF", "/Identity")
            EFF = encryption_entry.get("/EFF",  StmF)

            if StmF != "/Identity":
                StmF = filters[StmF]["/CFM"]
            if StrF != "/Identity":
                StrF = filters[StrF]["/CFM"]
            if EFF != "/Identity":
                EFF = filters[EFF]["/CFM"]

            allowed_methods = ("/Identity", "/V2", "/AESV2")
            if StmF not in allowed_methods:
                raise NotImplementedError("StmF Method %s NOT supported!" % StmF)
            if StrF not in allowed_methods:
                raise NotImplementedError("StrF Method %s NOT supported!" % StrF)
            if EFF not in allowed_methods:
                raise NotImplementedError("EFF Method %s NOT supported!" % EFF)

        R = encryption_entry["/R"]
        P = encryption_entry["/P"]
        Length = encryption_entry.get("/Length", 5 * 8)
        metadata_encrypted = encryption_entry.get("/EncryptMetadata", True)
        return Encryption(V, R, P, Length, metadata_encrypted, first_id_entry, StmF, StrF, EFF)
