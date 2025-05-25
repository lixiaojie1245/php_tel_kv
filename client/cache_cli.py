import os
import json
import base64
import requests
import argparse
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sympadding
from cryptography.hazmat.backends import default_backend
from hashlib import sha256

# 环境变量
SECRET = os.getenv('CACHE_SECRET')
SECRET = "woshiyigewifi"


if not SECRET:
    print("请设置环境变量 CACHE_SECRET")
    exit(1)

SERVER = os.getenv('CACHE_SERVER', 'http://localhost:8000')
SERVER="http://kv.fristvhost.xin/index.php"


def encrypt(plaintext: str) -> str:
    key = ''
    if SECRET != None:
        key = sha256(SECRET.encode()).digest()
    else:
        exit(1)

    iv = os.urandom(16)

    padder = sympadding.PKCS7(128).padder()
    padded_data = padder.update(plaintext.encode()) + padder.finalize()

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    return base64.b64encode(iv + encrypted).decode()


def decrypt(ciphertext_b64: str) -> str:
    try:
        raw = base64.b64decode(ciphertext_b64)
        iv, ct = raw[:16], raw[16:]

        key = ''
        if SECRET != None:
            key = sha256(SECRET.encode()).digest()
        else:
            exit(1)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        padded = decryptor.update(ct) + decryptor.finalize()

        unpadder = sympadding.PKCS7(128).unpadder()
        data = unpadder.update(padded) + unpadder.finalize()
        return data.decode()
    except Exception:
        return "[解密失败或数据格式错误]"


def set_key(key, value):
    encrypted_value = encrypt(value)
    res = requests.post(f"{SERVER}/set", json={"key": key, "value": encrypted_value})
    print(res.text)


def get_key(key):
    res = requests.get(f"{SERVER}/get", params={"key": key})
    d = (json.loads(res.text))
    d['value']=decrypt(d['value'])
    print(d)


def del_key(key):
    res = requests.post(f"{SERVER}/del", json={"key": key})
    print(res.text)


def list_keys():
    res = requests.get(f"{SERVER}/keys")
    print(res.text)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_set = subparsers.add_parser('set')
    parser_set.add_argument('key')
    parser_set.add_argument('value')

    parser_get = subparsers.add_parser('get')
    parser_get.add_argument('key')

    parser_del = subparsers.add_parser('del')
    parser_del.add_argument('key')

    subparsers.add_parser('keys')

    args = parser.parse_args()

    if args.command == 'set':
        set_key(args.key, args.value)
    elif args.command == 'get':
        get_key(args.key)
    elif args.command == 'del':
        del_key(args.key)
    elif args.command == 'keys':
        list_keys()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

