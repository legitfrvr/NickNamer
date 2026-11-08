import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import requests
import time
from concurrent.futures import ThreadPoolExecutor
from sites import SITES

UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
headers = {"User-Agent": UA}

TIMEOUT = 8
THREADS = 8

ok_sites = []
bad = 0
lang = "1"


def check(name, url):
    global bad
    try:
        res = requests.get(url, headers=headers, timeout=TIMEOUT)
        if res.status_code == 200:
            t = res.text.lower()
            if name == 'Instagram' and ("isn't available" in t or "page not found" in t or "broken" in t):
                print("[-]", name)
            elif name == 'Facebook' and ("isn't available" in t or "content not found" in t or "page not found" in t):
                print("[-]", name)
            elif name in ('Twitter', 'X') and ("doesn't exist" in t or "page not found" in t or "suspended" in t):
                print("[-]", name)
            elif name == 'TikTok' and ('10221' in res.text or "user not found" in t or ("couldn't find this account" in t and "uniqueid" not in t)):
                print("[-]", name)
            elif name == 'Threads' and ("isn't available" in t or "page not found" in t):
                print("[-]", name)
            elif name == 'Snapchat' and ("cannot find" in t or "doesn't exist" in t or "not found" in t):
                print("[-]", name)
            else:
                print("[+]", name, "->", url)
                ok_sites.append(url)
        elif res.status_code == 404:
            print("[-]", name)
        else:
            print("[?]", name, res.status_code)
    except requests.Timeout:
        bad += 1
        print("[!]", name, "таймаут" if lang == "1" else "timeout")
    except requests.exceptions.ConnectionError as e:
        if "resolve" in str(e).lower() or "getaddrinfo" in str(e).lower() or "name" in str(e).lower():
            print("[-]", name)
        else:
            bad += 1
            print("[!]", name, "ошибка:" if lang == "1" else "error:", type(e).__name__)
    except Exception as e:
        bad += 1
        print("[!]", name, "ошибка:" if lang == "1" else "error:", type(e).__name__)


def search(nick):
    global ok_sites, bad
    ok_sites = []
    bad = 0
    start = time.time()
    if lang == "1":
        print("ищу", nick, "по", len(SITES), "сайтам\n")
    else:
        print("searching", nick, "on", len(SITES), "sites\n")

    pool = ThreadPoolExecutor(max_workers=THREADS)
    for name, tmpl in SITES.items():
        pool.submit(check, name, tmpl.format(nick))
    pool.shutdown(wait=True)

    if lang == "1":
        print("\nпроверено:", len(SITES))
        print("найдено:", len(ok_sites))
        print("ошибок:", bad)
        print("время: %.1f сек" % (time.time() - start))
    else:
        print("\nchecked:", len(SITES))
        print("found:", len(ok_sites))
        print("errors:", bad)
        print("time: %.1f sec" % (time.time() - start))

    if ok_sites:
        with open('results.txt', 'a', encoding='utf-8') as f:
            f.write("\n--- " + nick + " ---\n")
            for u in ok_sites:
                f.write(u + "\n")
        if lang == "1":
            print("сохранил в results.txt")
        else:
            print("saved to results.txt")


def main():
    global lang
    print("NICK FINDER v0.2")
    c = input("1 - Русский, 2 - English: ").strip()
    if c == "2":
        lang = "2"
    else:
        lang = "1"

    while True:
        if lang == "1":
            nick = input("ник: ").strip()
        else:
            nick = input("nick: ").strip()

        if not nick:
            print("пустой ник" if lang == "1" else "empty nick")
        elif len(nick) > 50 or " " in nick:
            print("ник какой-то странный" if lang == "1" else "weird nick")
        else:
            search(nick)

        if lang == "1":
            again = input("Ещё один ник? (y/n): ").strip().lower()
        else:
            again = input("Another nick? (y/n): ").strip().lower()

        if again != "y" and again != "yes" and again != "д" and again != "да":
            break


if __name__ == '__main__':
    main()
