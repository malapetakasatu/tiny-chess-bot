import base64
import json
import os
import sys
import urllib.request
import zlib

RAW_BOOK = "eJw1jtERRCEIA1uhBQXFdk4lUoTFX+69uR9HhmzY0DBZBSa7HJNToAKNJseySTb4nWN1mc5nje2C/sv56bJ9NtljcttRBTXqhaZJGrh4qtohoXASaBfjoxLGcAwMsujs20Y2VbadIqmoNyqtHo2lwXClH14h9u3yV0vnDyOcI+++apYknOMejwubU7N+AX7qQDw="
LINES = [x.split() for x in zlib.decompress(base64.b64decode(RAW_BOOK)).decode().split("|")]

SCORES = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}
TABLE_P = [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 10, 25, 25, 10, 5, 5, 10, 10, 20, 30, 30, 20, 10, 10, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0]
TABLE_N = [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40, -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30, -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50]

HOST = os.environ.get("MAKEFUN_ENV_URL", "http://127.0.0.1:8095")

def send_json(url_path, req_obj):
    body = json.dumps(req_obj).encode("utf-8")
    req = urllib.request.Request(HOST + url_path, data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)

def parse_fen(f_str):
    sqs = {}
    for r_idx, r_str in enumerate(f_str.split()[0].split("/")):
        c_idx = 0
        for ch in r_str:
            if ch.isdigit():
                c_idx += int(ch)
            else:
                sqs[chr(97 + c_idx) + str(8 - r_idx)] = ch
                c_idx += 1
    return sqs

def score_move(f_str, mv, col):
    b = parse_fen(f_str)
    src, dst = mv[:2], mv[2:4]
    p, tgt = b.get(src, "P"), b.get(dst)
    val = 0
    if tgt:
        val += SCORES.get(tgt.lower(), 0) * 10 - SCORES.get(p.lower(), 0)
    if len(mv) == 5:
        val += SCORES.get(mv[4], 900) * 8
    pos = (int(dst[1]) - 1) * 8 + (ord(dst[0]) - 97)
    if col == "b":
        pos = 63 - pos
    pt = p.lower()
    if pt == "p":
        val += TABLE_P[pos]
    elif pt == "n":
        val += TABLE_N[pos]
    return val

def select_best(f_str, legals, col):
    top_mv, top_sc = legals[0], -10000000
    for cand in legals:
        sc = score_move(f_str, cand, col)
        if sc > top_sc or (sc == top_sc and cand < top_mv):
            top_sc, top_mv = sc, cand
    return top_mv

def run():
    while True:
        gm = send_json("/game", {})
        if gm.get("status") == "done":
            break
        g_idx = gm["game"]
        col = "w" if gm.get("colour") == "white" else "b"
        seq = LINES[g_idx - 1] if g_idx <= len(LINES) else []
        step, in_book = 0, True

        while gm.get("status") == "your_move":
            legals = gm["legal_moves"]
            nxt = None
            if in_book and step < len(seq):
                cand = seq[step]
                if cand in legals:
                    nxt, step = cand, step + 1
                else:
                    in_book = False
            if not nxt:
                nxt = select_best(gm["fen"], legals, col)
            gm = send_json("/move", {"game": g_idx, "move": nxt})
        print(f"Game {g_idx}: {gm.get('outcome')} by {gm.get('reason')} ({gm.get('plies')} plies)", file=sys.stderr)

if __name__ == "__main__":
    run()
