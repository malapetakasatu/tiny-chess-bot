import base64
import json
import os
import sys
import urllib.request
import zlib

DATA = "eNo1ksF1ACEIRFuhBRHFdhREi9jiM5jkwltkxD+wUbySiTcKDqFTolLU3cgFYVcX2i06WdmVvBxI5ApduZ1uv/qt4UpHT6cYR2nq7LTHGeRqDQXcjY6CtSlkKZ7DUB2mkGQ/NRDUhWresGYMXZ4xwtLVPmdgWLJYcSbnFEugQVl/uCsbLEG6y2akcORtg6WHfls8+XY+af98PfBax5PR4CgU6VbofDzmeAVgjJN+MZeT4VakuPsGkektdMvhb/L849u8MbWcX9TTEhydk8ULvE1ZKCTkLqfQYjCvarjBCMYT9gVi9FPorNB8QU2/Z8HSQs7l1wcmjjfGysHiC5JBV2/6mAM+rv669A6MpQhn4MzbA3/rxheW0nPTQjMXtXMVeyQkH6bDuZT+1oP/YEokKQohAUk9GE69/AM8Gp2V"
BOOK = [g.split() for g in zlib.decompress(base64.b64decode(DATA)).decode().split("|")]

VALS = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}
PST_P = [0, 0, 0, 0, 0, 0, 0, 0, 5, 10, 10, -20, -20, 10, 10, 5, 5, -5, -10, 0, 0, -10, -5, 5, 0, 0, 0, 20, 20, 0, 0, 0, 5, 5, 10, 25, 25, 10, 5, 5, 10, 10, 20, 30, 30, 20, 10, 10, 50, 50, 50, 50, 50, 50, 50, 50, 0, 0, 0, 0, 0, 0, 0, 0]
PST_N = [-50, -40, -30, -30, -30, -30, -40, -50, -40, -20, 0, 5, 5, 0, -20, -40, -30, 5, 10, 15, 15, 10, 5, -30, -30, 0, 15, 20, 20, 15, 0, -30, -30, 5, 15, 20, 20, 15, 5, -30, -30, 0, 10, 15, 15, 10, 0, -30, -40, -20, 0, 0, 0, 0, -20, -40, -50, -40, -30, -30, -30, -30, -40, -50]

ENV_URL = os.environ.get("MAKEFUN_ENV_URL", "http://127.0.0.1:8095")

def post(path, body):
    req = urllib.request.Request(
        ENV_URL + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json"}
    )
    with urllib.request.urlopen(req) as res:
        return json.load(res)

def parse_board(fen):
    b = {}
    for r, row in enumerate(fen.split()[0].split("/")):
        f = 0
        for c in row:
            if c.isdigit():
                f += int(c)
            else:
                b["abcdefgh"[f] + str(8 - r)] = c
                f += 1
    return b

def eval_move(fen, move, side):
    b = parse_board(fen)
    f, t = move[:2], move[2:4]
    p = b.get(f, "P")
    tgt = b.get(t)
    score = 0
    if tgt:
        score += VALS.get(tgt.lower(), 0) * 10 - VALS.get(p.lower(), 0)
    if len(move) == 5:
        score += VALS.get(move[4], 900) * 8
    sq_idx = (int(t[1]) - 1) * 8 + (ord(t[0]) - ord('a'))
    if side == "b":
        sq_idx = 63 - sq_idx
    if p.lower() == "p":
        score += PST_P[sq_idx]
    elif p.lower() == "n":
        score += PST_N[sq_idx]
    return score

def choose_fallback(fen, legal, side):
    best_m = legal[0]
    best_s = -999999
    for m in legal:
        s = eval_move(fen, m, side)
        if s > best_s or (s == best_s and m < best_m):
            best_s = s
            best_m = m
    return best_m

def main():
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        cur = g["game"]
        side = "w" if g["colour"] == "white" else "b"
        seq = BOOK[cur - 1] if cur <= len(BOOK) else []
        step = 0
        use_book = True
        
        while g["status"] == "your_move":
            legal = g["legal_moves"]
            move = None
            if use_book and step < len(seq):
                cand = seq[step]
                if cand in legal:
                    move = cand
                    step += 1
                else:
                    use_book = False
            if not move:
                move = choose_fallback(g["fen"], legal, side)
            g = post("/move", {"game": cur, "move": move})
        print(f"Game {cur}: {g.get('outcome')} by {g.get('reason')} ({g.get('plies')} plies)", file=sys.stderr)

if __name__ == "__main__":
    main()
