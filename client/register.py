from cache_cli import get_key, set_key, del_key, list_keys

# 命令行接口
import sys
import gethost

argv = sys.argv
def main():
    if argv[1]== 'get' and len(argv) == 3:
        get_key(argv[2])
    if argv[1]== 'reg' and len(argv) == 3:
        set_key(argv[2],str(gethost.get_host()))


if __name__ == "__main__":
    main()

