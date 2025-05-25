from ftplib import FTP, error_perm
import os
import json

# FTP 服务器信息
FTP_HOST = 'hostname'
FTP_USER = 'et al'
FTP_PASS = 'et al'
REMOTE_DIR = '/'

# 要排除的文件名和扩展名
# EXCLUDE_FILES = {'exclude.txt', 'ignore_me.png'}
EXCLUDE_FILES = {'upload.py', '.upload_cache.json' }
EXCLUDE_EXTENSIONS = {'.py','.log', '.bak'}
# 排除目录规则（目录名匹配，不含路径）
EXCLUDE_DIR_NAMES = {'.git', 'a'}


# 本地路径
LOCAL_ROOT = '.'
CACHE_FILE = '.upload_cache.json'


def should_exclude_file(filepath):
    filename = os.path.basename(filepath)
    if filename in EXCLUDE_FILES:
        return True
    _, ext = os.path.splitext(filename)
    return ext in EXCLUDE_EXTENSIONS

def should_exclude_dir(dirname):
    return dirname in EXCLUDE_DIR_NAMES

def create_remote_dir(ftp, path):
    dirs = path.strip('/').split('/')
    current = ''
    for d in dirs:
        current += '/' + d
        try:
            ftp.cwd(current)
        except error_perm:
            ftp.mkd(current)
            ftp.cwd(current)

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

def upload_files_to_ftp():
    ftp = FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print(f"Connected to {FTP_HOST}")

    create_remote_dir(ftp, REMOTE_DIR)

    cache = load_cache()
    updated = False

    for root, dirs, files in os.walk(LOCAL_ROOT):
        # 处理排除目录
        dirs[:] = [d for d in dirs if not should_exclude_dir(d)]

        rel_dir = os.path.relpath(root, LOCAL_ROOT)
        if rel_dir == ".":
            rel_dir = ""
        remote_dir = os.path.join(REMOTE_DIR, rel_dir).replace('\\', '/')
        create_remote_dir(ftp, remote_dir)

        for fname in files:
            local_path = os.path.join(root, fname)
            rel_path = os.path.normpath(os.path.join(rel_dir, fname)).replace('\\', '/')

            if should_exclude_file(local_path):
                continue

            mtime = os.path.getmtime(local_path)
            if rel_path in cache and cache[rel_path] == mtime:
                continue  # 未修改，跳过

            with open(local_path, 'rb') as f:
                ftp.storbinary(f'STOR {os.path.join(remote_dir, fname).replace("\\", "/")}', f)
                print(f"Uploaded: {rel_path}")
                cache[rel_path] = mtime
                updated = True

    ftp.quit()
    if updated:
        save_cache(cache)
        print("Updated cache saved.")
    print("Finished selective upload.")

if __name__ == '__main__':
    upload_files_to_ftp()
