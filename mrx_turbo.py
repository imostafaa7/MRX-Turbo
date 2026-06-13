#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
███╗   ███╗██████╗ ██╗  ██╗
████╗ ████║██╔══██╗╚██╗██╔╝
██╔████╔██║██████╔╝ ╚███╔╝ 
██║╚██╔╝██║██╔══██╗ ██╔██╗ 
██║ ╚═╝ ██║██║  ██║██╔╝ ██╗
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
MRX - Advanced Bug Bounty Framework v4.0
"""

import os, sys, subprocess, shutil, threading, time, json, signal, argparse
import sqlite3, re, hashlib, random, socket, csv, io, gzip, base64, ssl
import struct, fcntl, termios, readline, atexit, select
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict, deque
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from contextlib import contextmanager
from urllib.parse import urlparse, urlencode, quote
from urllib.request import urlopen, Request
from urllib.error import URLError

# ══════════════════════════════════════════════════════
#  COLOR ENGINE — Full 256 + TrueColor
# ══════════════════════════════════════════════════════
class A:
    RST="\033[0m"; BOLD="\033[1m"; DIM="\033[2m"; ITAL="\033[3m"
    UND="\033[4m"; BLINK="\033[5m"; REV="\033[7m"; STRIKE="\033[9m"
    RED="\033[38;5;196m"; LRED="\033[38;5;203m"; ORG="\033[38;5;208m"
    YEL="\033[38;5;226m"; LYEL="\033[38;5;228m"; GRN="\033[38;5;82m"
    LGRN="\033[38;5;120m"; DGRN="\033[38;5;28m"; CYN="\033[38;5;51m"
    LCYN="\033[38;5;159m"; BLU="\033[38;5;33m"; LBLU="\033[38;5;75m"
    MAG="\033[38;5;201m"; LMAG="\033[38;5;219m"; PINK="\033[38;5;213m"
    WHT="\033[38;5;255m"; LWHT="\033[38;5;252m"; GRY="\033[38;5;245m"
    DGRY="\033[38;5;238m"; PURP="\033[38;5;135m"; TEAL="\033[38;5;43m"
    GOLD="\033[38;5;220m"; LIME="\033[38;5;154m"; ROSE="\033[38;5;204m"
    BG_BLK="\033[48;5;232m"; BG_RED="\033[48;5;88m"; BG_GRN="\033[48;5;22m"
    BG_BLU="\033[48;5;17m"; BG_CYN="\033[48;5;23m"; BG_YEL="\033[48;5;136m"
    BG_ORG="\033[48;5;130m"; BG_MAG="\033[48;5;53m"; BG_GRY="\033[48;5;235m"
    HIDE_C="\033[?25l"; SHOW_C="\033[?25h"; CLR="\033[2J"; HOME="\033[H"
    UP="\033[A"; CLRLN="\033[2K"; SAVE="\033[s"; REST="\033[u"

def p(c,t): return f"{c}{t}{A.RST}"
def bold(t): return f"{A.BOLD}{t}{A.RST}"
def dim(t):  return f"{A.DIM}{t}{A.RST}"

def strip_ansi(s):
    return re.sub(r'\033\[[0-9;]*[mABCDHJKsufnpR]', '', s)

def vlen(s): return len(strip_ansi(s))

def tw():
    return min(shutil.get_terminal_size((120,40)).columns, 118)

def center(text, w=None):
    w = w or tw()
    pad = max(0,(w-vlen(text))//2)
    return " "*pad+text

def grad(text, colors):
    if not colors or not text: return text
    out=""
    for i,ch in enumerate(text):
        out += f"{colors[int(i/max(len(text),1)*len(colors))%len(colors)]}{ch}"
    return out+A.RST

CYBER = [A.CYN,A.LCYN,A.BLU,A.LBLU,A.PURP,A.MAG]
FIRE  = [A.RED,A.LRED,A.ORG,A.YEL]
MATRIX= [A.DGRN,A.GRN,A.LGRN,A.LIME]
GOLD  = [A.ORG,A.GOLD,A.YEL,A.LYEL,A.GOLD]

# ══════════════════════════════════════════════════════
#  ANIMATED BANNER
# ══════════════════════════════════════════════════════
LOGO=[
"███╗   ███╗██████╗ ██╗  ██╗",
"████╗ ████║██╔══██╗╚██╗██╔╝",
"██╔████╔██║██████╔╝ ╚███╔╝ ",
"██║╚██╔╝██║██╔══██╗ ██╔██╗ ",
"██║ ╚═╝ ██║██║  ██║██╔╝ ██╗",
"╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝",
]

MATRIX_CHARS="ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789ABCDEF"

def matrix_rain_effect(lines=6, duration=1.2):
    """Matrix rain animation before banner"""
    w = min(tw(), 80)
    cols = w // 2
    drops = [random.randint(0, lines) for _ in range(cols)]
    end_t = time.time() + duration
    sys.stdout.write(A.HIDE_C)
    while time.time() < end_t:
        row = ""
        for i in range(cols):
            if random.random() < 0.1:
                ch = random.choice(MATRIX_CHARS)
                intensity = random.random()
                if intensity > 0.8:
                    row += p(A.WHT+A.BOLD, ch+" ")
                elif intensity > 0.4:
                    row += p(A.GRN, ch+" ")
                else:
                    row += p(A.DGRN+A.DIM, ch+" ")
            else:
                row += "  "
        sys.stdout.write("\r" + row[:w] + "\n")
        sys.stdout.flush()
        time.sleep(0.04)
        sys.stdout.write(f"\033[{lines}A")
    # Clear rain
    for _ in range(lines):
        sys.stdout.write(A.CLRLN+"\n")
    sys.stdout.write(f"\033[{lines}A")
    sys.stdout.flush()

def glitch_text(text, color, iterations=4):
    """Glitch animation for single line"""
    glitch_chars = "!@#$%^&*<>?/\\|{}[]~`"
    for i in range(iterations):
        glitched = ""
        for ch in text:
            if random.random() < 0.3:
                glitched += random.choice(glitch_chars)
            else:
                glitched += ch
        sys.stdout.write(f"\r{center(p(color, glitched))}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write(f"\r{center(p(color, text))}\n")
    sys.stdout.flush()

def typewriter(text, color=None, delay=0.018):
    """Typewriter effect for text"""
    for ch in text:
        sys.stdout.write(p(color, ch) if color else ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_banner(animated=True):
    os.system("clear")
    sys.stdout.write(A.HIDE_C)

    if animated:
        matrix_rain_effect(5, 0.8)

    print()
    logo_colors = [A.CYN,A.LCYN,A.BLU,A.PURP,A.MAG,A.PINK]
    for i, line in enumerate(LOGO):
        c = logo_colors[i % len(logo_colors)]
        if animated:
            # Slide in from left
            padded = center(line)
            visible = ""
            for ch in padded:
                visible += ch
                sys.stdout.write(f"\r{p(c+A.BOLD, visible)}")
                sys.stdout.flush()
                time.sleep(0.003)
            print()
        else:
            print(center(p(logo_colors[i], line)))

    print()
    if animated:
        glitch_text("Advanced Bug Bounty Framework v4.0", A.YEL+A.BOLD, 3)
        time.sleep(0.1)
        glitch_text("[ Reconnaissance · Scanning · Exploitation · Reporting ]", A.GRY, 2)
    else:
        print(center(p(A.YEL+A.BOLD, "Advanced Bug Bounty Framework v4.0")))
        print(center(p(A.GRY, "[ Reconnaissance · Scanning · Exploitation · Reporting ]")))

    print()
    w = min(tw(), 110)
    feats = [
        p(A.GRN,  "⬡ Auto-Proxy"),
        p(A.CYN,  "⬡ Smart Install"),
        p(A.YEL,  "⬡ Live Dashboard"),
        p(A.MAG,  "⬡ SQLite DB"),
        p(A.ORG,  "⬡ Parallel Scan"),
        p(A.PINK, "⬡ Auto-Report"),
        p(A.LIME, "⬡ 12 Modules"),
    ]
    feat_line = "  " + "   ".join(feats)
    border_top = p(A.CYN+A.DIM, "┌"+"─"*(w-2)+"┐")
    border_bot = p(A.CYN+A.DIM, "└"+"─"*(w-2)+"┘")
    border_mid = p(A.CYN+A.DIM, "│")
    inner = center(feat_line, w-2)
    print(border_top)
    print(f"{border_mid}{inner}{border_mid}")
    print(border_bot)
    print()
    sys.stdout.write(A.SHOW_C)

# ══════════════════════════════════════════════════════
#  SPINNER SYSTEM — 8 styles
# ══════════════════════════════════════════════════════
SPIN_STYLES = {
    "cyber":   ["◈","◉","◎","○","◎","◉"],
    "dots":    ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"],
    "bounce":  ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"],
    "arc":     ["◜","◠","◝","◞","◡","◟"],
    "arrows":  ["←","↖","↑","↗","→","↘","↓","↙"],
    "pulse":   ["█","▓","▒","░","▒","▓"],
    "scan":    ["▱▱▱▱▱","▰▱▱▱▱","▰▰▱▱▱","▰▰▰▱▱","▰▰▰▰▱","▰▰▰▰▰"],
    "radar":   ["🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"],
}

class Spin:
    def __init__(self, msg="", style="dots", color=None):
        self.msg=msg; self.frames=SPIN_STYLES.get(style,SPIN_STYLES["dots"])
        self.color=color or A.CYN; self._stop=threading.Event()
        self._t=threading.Thread(target=self._run,daemon=True)
        self.ok=True; self._sub=""

    def _run(self):
        i=0
        while not self._stop.is_set():
            f=self.frames[i%len(self.frames)]
            sub=f"  {p(A.GRY,self._sub)}" if self._sub else ""
            sys.stdout.write(f"\r  {p(self.color,f)}  {p(A.WHT,self.msg)}{p(A.GRY,' ...')}{sub}   ")
            sys.stdout.flush(); time.sleep(0.08); i+=1

    def sub(self,s): self._sub=s; return self
    def update(self,m): self.msg=m; return self
    def start(self): self._t.start(); return self
    def stop(self,ok=True):
        self._stop.set(); self._t.join(0.5)
        icon=p(A.GRN,"✔") if ok else p(A.RED,"✘")
        suf=p(A.GRN," done") if ok else p(A.RED," failed")
        sys.stdout.write(f"\r  {icon}  {p(A.WHT,self.msg)}{suf}{' '*30}\n")
        sys.stdout.flush()
    def __enter__(self): return self.start()
    def __exit__(self,*a): self.stop(self.ok)

def pbar(cur, tot, lbl="", w=38):
    pct=min(cur/max(tot,1),1.0); done=int(pct*w)
    bar=p(A.CYN,"█"*done)+p(A.DGRY,"░"*(w-done))
    print(f"\r  {bar}  {p(A.YEL,f'{pct*100:5.1f}%')}  {p(A.GRY,lbl[:35])}",end="",flush=True)

# ══════════════════════════════════════════════════════
#  LOGGING
# ══════════════════════════════════════════════════════
_log_file=None; _llock=threading.Lock()

def _wlog(msg):
    if _log_file:
        with _llock:
            with open(_log_file,"a",errors="replace") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {strip_ansi(msg)}\n")

def li(m):  s=f"  {p(A.BLU,'ℹ')}  {p(A.LWHT,m)}"; print(s); _wlog(s)
def lok(m): s=f"  {p(A.GRN,'✔')}  {p(A.GRN,m)}";  print(s); _wlog(s)
def lw(m):  s=f"  {p(A.YEL,'⚠')}  {p(A.YEL,m)}";  print(s); _wlog(s)
def le(m):  s=f"  {p(A.RED,'✘')}  {p(A.RED,m)}";   print(s); _wlog(s)

SEV_IC={"critical":"💀","high":"🔥","medium":"⚡","low":"🔔","info":"◈"}
SEV_CL={"critical":A.RED+A.BOLD,"high":A.LRED,"medium":A.ORG,"low":A.YEL,"info":A.BLU}

def lfound(m,sev="info"):
    ic=SEV_IC.get(sev,"◈"); cl=SEV_CL.get(sev,A.MAG)
    s=f"  {ic}  {p(cl,m)}"; print(s); _wlog(s)

def lstep(n,title):
    w=min(tw(),110)
    print(f"\n{p(A.CYN+A.DIM,'═'*w)}")
    print(f"  {p(A.BG_BLU+A.WHT+A.BOLD,f' MODULE {n:02d} ')}  {p(A.CYN+A.BOLD,title.upper())}")
    print(p(A.CYN+A.DIM,"═"*w))

def lsec(title,icon="◈"):
    w=min(tw(),110)
    print(f"\n  {p(A.GRY+A.DIM,'─'*w)}")
    print(f"  {icon}  {p(A.CYN+A.BOLD,title)}")
    print(f"  {p(A.GRY+A.DIM,'─'*w)}")

# ══════════════════════════════════════════════════════
#  SQLITE DATABASE
# ══════════════════════════════════════════════════════
class DB:
    def __init__(self, path):
        self.path=path
        self.conn=sqlite3.connect(path,check_same_thread=False)
        self._lock=threading.Lock(); self._init()

    def _init(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS scans(
            id INTEGER PRIMARY KEY, domain TEXT, started TEXT,
            finished TEXT, status TEXT DEFAULT 'running', config TEXT);
        CREATE TABLE IF NOT EXISTS subdomains(
            id INTEGER PRIMARY KEY, sid INTEGER,
            host TEXT, ip TEXT, alive INTEGER DEFAULT 0,
            code INTEGER, title TEXT, tech TEXT, source TEXT, ts TEXT,
            UNIQUE(sid,host));
        CREATE TABLE IF NOT EXISTS ports(
            id INTEGER PRIMARY KEY, sid INTEGER,
            host TEXT, port INTEGER, proto TEXT,
            service TEXT, version TEXT,
            UNIQUE(sid,host,port));
        CREATE TABLE IF NOT EXISTS urls(
            id INTEGER PRIMARY KEY, sid INTEGER,
            url TEXT, source TEXT, ptype TEXT,
            UNIQUE(sid,url));
        CREATE TABLE IF NOT EXISTS findings(
            id INTEGER PRIMARY KEY, sid INTEGER,
            vtype TEXT, severity TEXT, url TEXT,
            title TEXT, desc TEXT, tool TEXT, ts TEXT);
        CREATE TABLE IF NOT EXISTS dirs(
            id INTEGER PRIMARY KEY, sid INTEGER,
            url TEXT, code INTEGER, size INTEGER,
            UNIQUE(sid,url));
        CREATE TABLE IF NOT EXISTS proxies(
            id INTEGER PRIMARY KEY, addr TEXT,
            ptype TEXT, latency REAL, alive INTEGER DEFAULT 0,
            last_check TEXT, used INTEGER DEFAULT 0);
        CREATE TABLE IF NOT EXISTS screenshots(
            id INTEGER PRIMARY KEY, sid INTEGER,
            url TEXT, path TEXT, ts TEXT);
        CREATE INDEX IF NOT EXISTS ix_f_sev ON findings(severity);
        CREATE INDEX IF NOT EXISTS ix_f_type ON findings(vtype);
        """)
        self.conn.commit()

    def new_scan(self, domain, cfg):
        with self._lock:
            c=self.conn.cursor()
            c.execute("INSERT INTO scans(domain,started,config) VALUES(?,?,?)",
                      (domain,datetime.now().isoformat(),json.dumps(cfg)))
            self.conn.commit(); return c.lastrowid

    def finish_scan(self,sid):
        with self._lock:
            self.conn.execute("UPDATE scans SET finished=?,status='done' WHERE id=?",
                              (datetime.now().isoformat(),sid))
            self.conn.commit()

    def add_sub(self,sid,host,**kw):
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO subdomains(sid,host,ip,alive,code,title,tech,source,ts)"
                    " VALUES(?,?,?,?,?,?,?,?,?)",
                    (sid,host,kw.get('ip',''),kw.get('alive',0),kw.get('code',0),
                     kw.get('title','')[:120],kw.get('tech','')[:200],
                     kw.get('source','enum'),datetime.now().isoformat()))
                self.conn.commit()
            except: pass

    def add_port(self,sid,host,port,**kw):
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO ports(sid,host,port,proto,service,version)"
                    " VALUES(?,?,?,?,?,?)",
                    (sid,host,port,kw.get('proto','tcp'),
                     kw.get('service',''),kw.get('version','')))
                self.conn.commit()
            except: pass

    def add_url(self,sid,url,src='',pt=''):
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO urls(sid,url,source,ptype) VALUES(?,?,?,?)",
                    (sid,url,src,pt))
                self.conn.commit()
            except: pass

    def add_finding(self,sid,**kw):
        with self._lock:
            self.conn.execute(
                "INSERT INTO findings(sid,vtype,severity,url,title,desc,tool,ts)"
                " VALUES(?,?,?,?,?,?,?,?)",
                (sid,kw.get('type',''),kw.get('severity','info'),kw.get('url',''),
                 kw.get('title','')[:200],kw.get('desc','')[:500],
                 kw.get('tool',''),datetime.now().isoformat()))
            self.conn.commit()

    def add_dir(self,sid,url,code=200,size=0):
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO dirs(sid,url,code,size) VALUES(?,?,?,?)",
                    (sid,url,code,size))
                self.conn.commit()
            except: pass

    def add_proxy(self,addr,ptype='http',latency=0,alive=0):
        with self._lock:
            try:
                self.conn.execute(
                    "INSERT OR IGNORE INTO proxies(addr,ptype,latency,alive,last_check)"
                    " VALUES(?,?,?,?,?)",
                    (addr,ptype,latency,alive,datetime.now().isoformat()))
                self.conn.commit()
            except:
                self.conn.execute(
                    "UPDATE proxies SET latency=?,alive=?,last_check=? WHERE addr=?",
                    (latency,alive,datetime.now().isoformat(),addr))
                self.conn.commit()

    def get_alive_proxies(self):
        return self.conn.execute(
            "SELECT addr,ptype FROM proxies WHERE alive=1 ORDER BY latency ASC").fetchall()

    def stats(self,sid):
        c=self.conn.cursor()
        return {k:c.execute(q,(sid,)).fetchone()[0] for k,q in [
            ('subs',  "SELECT COUNT(*) FROM subdomains WHERE sid=?"),
            ('alive', "SELECT COUNT(*) FROM subdomains WHERE sid=? AND alive=1"),
            ('ports', "SELECT COUNT(*) FROM ports WHERE sid=?"),
            ('urls',  "SELECT COUNT(*) FROM urls WHERE sid=?"),
            ('finds', "SELECT COUNT(*) FROM findings WHERE sid=?"),
            ('crit',  "SELECT COUNT(*) FROM findings WHERE sid=? AND severity='critical'"),
            ('high',  "SELECT COUNT(*) FROM findings WHERE sid=? AND severity='high'"),
            ('dirs',  "SELECT COUNT(*) FROM dirs WHERE sid=?"),
        ]}

    def close(self): self.conn.close()

# ══════════════════════════════════════════════════════
#  LIVE DASHBOARD — Animated Real-time Panel
# ══════════════════════════════════════════════════════
class Dashboard:
    PULSE=["▁","▂","▃","▄","▅","▆","▇","█","▇","▆","▅","▄","▃","▂"]
    SCAN_ANIM=["⠋⠋⠋","⠙⠙⠙","⠹⠹⠹","⠸⠸⠸","⠼⠼⠼","⠴⠴⠴"]

    def __init__(self,db,sid,domain):
        self.db=db; self.sid=sid; self.domain=domain
        self._stop=threading.Event(); self._lines=0
        self._current_step="Initializing"
        self._history=deque(maxlen=50)
        self._t=threading.Thread(target=self._run,daemon=True)
        self._lock=threading.Lock(); self._tick=0

    def set_step(self,s): self._current_step=s

    def add_event(self,msg,sev="info"):
        icon=SEV_IC.get(sev,"◈"); cl=SEV_CL.get(sev,A.GRY)
        self._history.append(f"  {icon} {p(cl,msg[:60])}")

    def start(self): self._t.start()
    def stop(self):
        self._stop.set(); self._t.join(1)
        with self._lock:
            if self._lines>0:
                sys.stdout.write(f"\033[{self._lines}A")
            for _ in range(self._lines):
                sys.stdout.write(A.CLRLN+"\n")
            if self._lines>0:
                sys.stdout.write(f"\033[{self._lines}A")
            sys.stdout.flush(); self._lines=0

    def _run(self):
        while not self._stop.is_set():
            self._render(); self._tick+=1; time.sleep(0.25)

    def _render(self):
        st=self.db.stats(self.sid)
        w=min(tw(),110); t=self._tick
        lines=[]
        pulse_f=self.PULSE[t%len(self.PULSE)]
        scan_f =self.SCAN_ANIM[t%len(self.SCAN_ANIM)]

        # Top border with animation
        left_anim  = p(A.CYN, "◄"*(1+(t%3)))
        right_anim = p(A.CYN, "►"*(1+(t%3)))
        title_mid  = p(A.CYN+A.BOLD," MRX LIVE DASHBOARD ")
        lines.append(p(A.CYN+A.DIM,"╔"+"═"*(w-2)+"╗"))
        lines.append(p(A.CYN+A.DIM,"║")+center(
            f"{left_anim}{title_mid}{right_anim}  "
            f"{p(A.GRN+A.BLINK,pulse_f)}  {dim(self.domain[:30])}",w-2
        )+p(A.CYN+A.DIM,"║"))
        lines.append(p(A.CYN+A.DIM,"╠"+"═"*(w-2)+"╣"))

        # Stats row with mini bars
        def sbox(lbl,val,color,maxv=None):
            bar=""
            if maxv and maxv>0:
                pct=min(val/maxv,1.0)
                bar=" "+p(color,"▪"*int(pct*5))+p(A.DGRY,"▫"*int((1-pct)*5))
            return f" {p(A.GRY,lbl+':')} {p(color+A.BOLD,str(val))}{bar} "

        row1="  "+sbox("Subs",st['subs'],A.BLU)+p(A.GRY,"│")+\
             sbox("Alive",st['alive'],A.GRN)+p(A.GRY,"│")+\
             sbox("Ports",st['ports'],A.ORG)+p(A.GRY,"│")+\
             sbox("URLs",st['urls'],A.CYN)+p(A.GRY,"│")+\
             sbox("Dirs",st['dirs'],A.PURP)
        row2="  "+sbox("Findings",st['finds'],A.YEL)+p(A.GRY,"│")+\
             sbox("Critical",st['crit'],A.RED)+p(A.GRY,"│")+\
             sbox("High",st['high'],A.LRED)+p(A.GRY,"│")+\
             f" {p(A.GRY,'Module:')} {p(A.YEL+A.BOLD,self._current_step[:25])} {p(A.CYN,scan_f)} "

        lines.append(p(A.CYN+A.DIM,"║")+f"{row1}"+p(A.CYN+A.DIM,"║"))
        lines.append(p(A.CYN+A.DIM,"║")+f"{row2}"+p(A.CYN+A.DIM,"║"))

        # Recent events
        lines.append(p(A.CYN+A.DIM,"╠"+"─"*(w-2)+"╣"))
        recent=list(self._history)[-2:] if self._history else [p(A.GRY,"  waiting for results...")]
        for ev in recent:
            padded=ev+" "*(w-2-vlen(ev)-2)
            lines.append(p(A.CYN+A.DIM,"║")+f" {padded} "+p(A.CYN+A.DIM,"║"))
        while len([l for l in lines if "╠" not in strip_ansi(l) and "╔" not in strip_ansi(l) and "╚" not in strip_ansi(l)])<6:
            lines.append(p(A.CYN+A.DIM,"║")+" "*(w-2)+p(A.CYN+A.DIM,"║"))

        lines.append(p(A.CYN+A.DIM,"╚"+"═"*(w-2)+"╝"))

        with self._lock:
            if self._lines>0: sys.stdout.write(f"\033[{self._lines}A")
            for line in lines:
                sys.stdout.write(A.CLRLN+line+"\n")
            sys.stdout.flush(); self._lines=len(lines)

# ══════════════════════════════════════════════════════
#  PROXY MANAGER — Auto-fetch, test, rotate
# ══════════════════════════════════════════════════════
class ProxyManager:
    SOURCES=[
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    ]
    TEST_URL="http://httpbin.org/ip"

    def __init__(self,db:DB,outdir:Path):
        self.db=db; self.outdir=outdir
        self.proxies:List[str]=[]; self._idx=0; self._lock=threading.Lock()
        self.proxy_file=outdir/"proxies.txt"
        self.alive_file=outdir/"proxies_alive.txt"

    def fetch_public_proxies(self, limit=500) -> int:
        """Download proxies from public sources"""
        lsec("PROXY DOWNLOADER","🌐")
        collected=set()

        for i,src in enumerate(self.SOURCES):
            sp=Spin(f"Fetching from source {i+1}/{len(self.SOURCES)}","arc",A.CYN)
            sp.start()
            try:
                req=Request(src,headers={"User-Agent":"Mozilla/5.0"},method="GET")
                ctx=ssl.create_default_context(); ctx.check_hostname=False
                ctx.verify_mode=ssl.CERT_NONE
                with urlopen(req,timeout=15,context=ctx) as r:
                    content=r.read().decode(errors="replace")
                    for line in content.splitlines():
                        line=line.strip()
                        if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}$',line):
                            collected.add(line)
                sp.stop(True)
            except Exception as ex:
                sp.stop(False); lw(f"Source {i+1} failed: {ex}")
            if len(collected)>=limit: break

        proxies=list(collected)[:limit]
        self.proxy_file.write_text("\n".join(proxies))
        lok(f"Collected {p(A.YEL+A.BOLD,str(len(proxies)))} proxies from public sources")
        return len(proxies)

    def test_proxies(self, proxies:List[str]=None, max_workers:int=80,
                     timeout:int=6) -> List[str]:
        """Test proxies in parallel"""
        if proxies is None:
            if self.proxy_file.exists():
                proxies=self.proxy_file.read_text().splitlines()
            else:
                proxies=[]
        if not proxies:
            lw("No proxies to test"); return []

        lsec(f"TESTING {len(proxies)} PROXIES","⚡")
        alive=[]; dead=0
        lock=threading.Lock(); tested=0
        sem=threading.Semaphore(max_workers)

        def _test(proxy):
            nonlocal tested,dead
            with sem:
                t0=time.time()
                try:
                    ip,port_s=proxy.rsplit(":",1); port=int(port_s)
                    sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    sock.settimeout(timeout)
                    sock.connect((ip,port)); sock.close()
                    latency=round((time.time()-t0)*1000,1)
                    with lock:
                        alive.append(proxy)
                        self.db.add_proxy(proxy,'http',latency,1)
                except:
                    dead+=1
                    with lock: self.db.add_proxy(proxy,'http',9999,0)
                finally:
                    with lock:
                        tested+=1
                        pbar(tested,len(proxies),f"alive:{len(alive)} dead:{dead}")

        threads=[threading.Thread(target=_test,args=(prx,),daemon=True)
                 for prx in proxies]
        for t in threads: t.start()
        for t in threads: t.join()
        print()

        alive.sort(key=lambda x: self.db.conn.execute(
            "SELECT latency FROM proxies WHERE addr=?",(x,)).fetchone()[0] or 9999)

        self.alive_file.write_text("\n".join(alive))
        self.proxies=alive
        lok(f"Alive proxies: {p(A.GRN+A.BOLD,str(len(alive)))} / {len(proxies)}")
        return alive

    def load_from_file(self, path:str) -> int:
        """Load proxies from user file"""
        try:
            lines=[l.strip() for l in Path(path).read_text().splitlines() if l.strip()]
            valid=[l for l in lines if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$',l)]
            self.proxy_file.write_text("\n".join(valid))
            lok(f"Loaded {len(valid)} proxies from {path}")
            return len(valid)
        except Exception as e:
            le(f"Failed to load proxies: {e}"); return 0

    def next(self) -> Optional[str]:
        """Round-robin proxy rotation"""
        if not self.proxies: return None
        with self._lock:
            proxy=self.proxies[self._idx % len(self.proxies)]
            self._idx+=1; return proxy

    def get_env(self) -> dict:
        """Get proxy env vars for subprocess"""
        proxy=self.next()
        if not proxy: return {}
        url=f"http://{proxy}"
        return {"http_proxy":url,"https_proxy":url,"HTTP_PROXY":url,"HTTPS_PROXY":url}

    def get_curl_flag(self) -> str:
        proxy=self.next()
        return f"--proxy {proxy}" if proxy else ""

    def interactive_menu(self):
        """Interactive proxy setup menu"""
        lsec("PROXY CONFIGURATION","🔧")
        opts=[
            ("1", "Auto-download from public sources (free proxies)"),
            ("2", "Load from file"),
            ("3", "Add single proxy manually"),
            ("4", "Test existing proxies"),
            ("5", "Skip proxy setup"),
        ]
        for num,desc in opts:
            print(f"    {p(A.CYN,num+'.')}  {p(A.LWHT,desc)}")
        print()
        choice=input(f"  {p(A.CYN,'⟩')} Select: ").strip()

        if choice=="1":
            n=self.fetch_public_proxies(800)
            if n>0:
                li("Testing proxies (this may take a moment)...")
                proxies=self.proxy_file.read_text().splitlines()
                self.test_proxies(proxies,max_workers=100,timeout=5)
        elif choice=="2":
            path=input(f"  {p(A.CYN,'⟩')} Proxy file path: ").strip()
            if path and Path(path).exists():
                self.load_from_file(path)
                proxies=self.proxy_file.read_text().splitlines()
                self.test_proxies(proxies)
        elif choice=="3":
            proxy=input(f"  {p(A.CYN,'⟩')} Enter proxy (IP:PORT): ").strip()
            if re.match(r'^\d+\.\d+\.\d+\.\d+:\d+$',proxy):
                self.proxies=[proxy]
                lok(f"Using proxy: {proxy}")
        elif choice=="4":
            if self.proxy_file.exists():
                proxies=self.proxy_file.read_text().splitlines()
                self.test_proxies(proxies)
            else:
                lw("No proxy file found")
        else:
            li("Skipping proxy setup — direct connection")

# ══════════════════════════════════════════════════════
#  TOOL MANAGER — Auto-install everything
# ══════════════════════════════════════════════════════
@dataclass
class Tool:
    name:str; desc:str
    apt:str=None; go_pkg:str=None
    pip_pkg:str=None; git_url:str=None
    required:bool=True

TOOLS:Dict[str,Tool]={
    "subfinder":  Tool("subfinder","Subdomain enumeration",
                       go_pkg="github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"),
    "amass":      Tool("amass","OSINT subdomain discovery",apt="amass"),
    "assetfinder":Tool("assetfinder","Fast subdomain finder",
                       go_pkg="github.com/tomnomnom/assetfinder@latest"),
    "httpx":      Tool("httpx","Live host detection",
                       go_pkg="github.com/projectdiscovery/httpx/cmd/httpx@latest"),
    "nmap":       Tool("nmap","Port/service scanner",apt="nmap"),
    "naabu":      Tool("naabu","Fast port scanner",
                       go_pkg="github.com/projectdiscovery/naabu/v2/cmd/naabu@latest"),
    "masscan":    Tool("masscan","High-speed scanner",apt="masscan",required=False),
    "ffuf":       Tool("ffuf","Web fuzzer",
                       go_pkg="github.com/ffuf/ffuf/v2@latest"),
    "feroxbuster":Tool("feroxbuster","Recursive fuzzer",apt="feroxbuster",required=False),
    "gobuster":   Tool("gobuster","Dir/DNS brute",apt="gobuster",required=False),
    "gau":        Tool("gau","URL collector",
                       go_pkg="github.com/lc/gau/v2/cmd/gau@latest"),
    "waybackurls":Tool("waybackurls","Wayback URLs",
                       go_pkg="github.com/tomnomnom/waybackurls@latest"),
    "hakrawler":  Tool("hakrawler","Web crawler",
                       go_pkg="github.com/hakluke/hakrawler@latest"),
    "katana":     Tool("katana","Advanced crawler",
                       go_pkg="github.com/projectdiscovery/katana/cmd/katana@latest"),
    "gf":         Tool("gf","URL pattern filter",
                       go_pkg="github.com/tomnomnom/gf@latest"),
    "qsreplace":  Tool("qsreplace","Query string replacer",
                       go_pkg="github.com/tomnomnom/qsreplace@latest"),
    "anew":       Tool("anew","Append unique lines",
                       go_pkg="github.com/tomnomnom/anew@latest"),
    "nuclei":     Tool("nuclei","Vuln scanner",
                       go_pkg="github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"),
    "dalfox":     Tool("dalfox","XSS scanner",
                       go_pkg="github.com/hahwul/dalfox/v2@latest"),
    "sqlmap":     Tool("sqlmap","SQLi tool",apt="sqlmap"),
    "nikto":      Tool("nikto","Web server scanner",apt="nikto"),
    "subzy":      Tool("subzy","Takeover checker",
                       go_pkg="github.com/PentestPad/subzy@latest"),
    "dnsx":       Tool("dnsx","DNS resolver",
                       go_pkg="github.com/projectdiscovery/dnsx/cmd/dnsx@latest"),
    "notify":     Tool("notify","Notifications",
                       go_pkg="github.com/projectdiscovery/notify/cmd/notify@latest",
                       required=False),
    "wpscan":     Tool("wpscan","WordPress scanner",apt="wpscan",required=False),
    "testssl.sh": Tool("testssl.sh","SSL/TLS tester",apt="testssl.sh",required=False),
}

def avail(name:str)->bool: return shutil.which(name) is not None

def _install_go(pkg,name)->bool:
    if not avail("go"):
        subprocess.run(["sudo","apt","install","-y","golang-go"],
                       capture_output=True,timeout=120)
    gopath=Path.home()/"go"
    env={**os.environ,"GOPATH":str(gopath),"GO111MODULE":"on","GOFLAGS":"-mod=mod"}
    r=subprocess.run(["go","install",pkg],capture_output=True,env=env,timeout=240)
    bin_path=gopath/"bin"/name
    if bin_path.exists():
        subprocess.run(["sudo","cp",str(bin_path),f"/usr/local/bin/{name}"],
                       capture_output=True)
    return bin_path.exists() or avail(name)

def _install_apt(pkg)->bool:
    r=subprocess.run(["sudo","apt","install","-y","--no-install-recommends",pkg],
                     capture_output=True,timeout=300,
                     env={**os.environ,"DEBIAN_FRONTEND":"noninteractive"})
    return r.returncode==0

def install_tool(name:str,tool:Tool)->bool:
    if tool.apt:    return _install_apt(tool.apt)
    if tool.go_pkg: return _install_go(tool.go_pkg,name)
    if tool.pip_pkg:
        r=subprocess.run([sys.executable,"-m","pip","install",
                          tool.pip_pkg,"--break-system-packages"],
                         capture_output=True,timeout=120)
        return r.returncode==0
    return False

def check_tools(names:List[str], auto:bool=False, db:DB=None)->Dict[str,bool]:
    lsec("TOOL CHECKER & INSTALLER","🔧")
    status={}; missing=[]

    for name in names:
        tool=TOOLS.get(name)
        if not tool: continue
        ok=avail(name); status[name]=ok
        icon=p(A.GRN,"✔") if ok else p(A.YEL,"✗")
        req=p(A.GRY," [opt]") if not tool.required else ""
        print(f"  {icon}  {p(A.WHT if ok else A.GRY,name):<28}{p(A.DGRY,tool.desc)}{req}")
        if not ok: missing.append(name)

    if not missing:
        lok(f"All {len(names)} tools ready!"); return status

    print(); lw(f"Missing {len(missing)} tools: {p(A.GRY,', '.join(missing))}")

    if not auto:
        ans=input(f"\n  {p(A.CYN,'⟩')} Install missing tools? {p(A.GRY,'[Y/n]')}: ").strip().lower()
        if ans=="n":
            lw("Skipping — some modules may fail"); return status

    print()
    # Install in parallel for apt, sequential for Go
    apt_missing=[n for n in missing if TOOLS[n].apt]
    go_missing =[n for n in missing if TOOLS[n].go_pkg and not TOOLS[n].apt]

    # Batch apt install
    if apt_missing:
        sp=Spin(f"apt install: {', '.join(apt_missing)}","bounce",A.GRN)
        sp.start()
        pkgs=[TOOLS[n].apt for n in apt_missing]
        r=subprocess.run(
            ["sudo","apt","install","-y","--no-install-recommends"]+pkgs,
            capture_output=True,timeout=400,
            env={**os.environ,"DEBIAN_FRONTEND":"noninteractive"})
        sp.stop(r.returncode==0)
        for n in apt_missing: status[n]=avail(n)

    # Go packages
    for name in go_missing:
        tool=TOOLS[name]
        sp=Spin(f"go install: {name}","arc",A.CYN); sp.start()
        ok=_install_go(tool.go_pkg,name); sp.stop(ok)
        status[name]=ok

    # Install seclists if missing
    if not Path("/usr/share/seclists").exists():
        sp=Spin("Installing seclists wordlists","bounce",A.YEL); sp.start()
        ok=_install_apt("seclists"); sp.stop(ok)

    # Install gf patterns
    if avail("gf"):
        gf_patterns=Path.home()/".gf"
        if not gf_patterns.exists() or not list(gf_patterns.glob("*.json")):
            sp=Spin("Installing gf patterns","arc",A.CYN); sp.start()
            r=subprocess.run(
                "git clone https://github.com/1ndianl33t/Gf-Patterns ~/.gf 2>/dev/null || true",
                shell=True,capture_output=True,timeout=60)
            sp.stop(True)

    return status

# ══════════════════════════════════════════════════════
#  WORDLISTS
# ══════════════════════════════════════════════════════
WL_PATHS={
    "common":["/usr/share/wordlists/dirb/common.txt",
              "/usr/share/seclists/Discovery/Web-Content/common.txt"],
    "medium":["/usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt",
              "/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt"],
    "large": ["/usr/share/seclists/Discovery/Web-Content/raft-large-words.txt"],
    "dns":   ["/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt",
              "/usr/share/seclists/Discovery/DNS/dns-Jhaddix.txt"],
    "params":["/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt"],
    "lfi":   ["/usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt"],
    "xss":   ["/usr/share/seclists/Fuzzing/XSS/XSS-Jhaddix.txt"],
    "sqli":  ["/usr/share/seclists/Fuzzing/SQLi/Generic-SQLi.txt"],
}

def wl(kind="common")->Optional[str]:
    for path in WL_PATHS.get(kind,[]):
        if Path(path).exists(): return path
    # Generate fallback
    fallback=Path(f"/tmp/mrx_wl_{kind}.txt")
    if not fallback.exists():
        words={"common":["admin","login","api","config","backup",".git","robots.txt",
                         "dashboard","upload","files","static","js","css","v1","v2",
                         "api/v1","api/v2","graphql","swagger","actuator","metrics",
                         "health","status","debug","test","dev","staging","phpmyadmin",
                         "wp-admin","wp-content","xmlrpc.php",".env",".htaccess"],
               "dns":["www","mail","ftp","vpn","api","dev","staging","test","admin",
                       "portal","app","dashboard","cdn","assets","static","m","mobile"],
               }.get(kind,["admin","api","login","config"])
        fallback.write_text("\n".join(words))
    return str(fallback)

# ══════════════════════════════════════════════════════
#  COMMAND RUNNER — Proxy-aware
# ══════════════════════════════════════════════════════
def run(cmd:str, outfile:str=None, timeout:int=300,
        proxy_env:dict=None, stdin:str=None)->Tuple[bool,str]:
    try:
        env={**os.environ,**(proxy_env or {})}
        proc=subprocess.run(
            cmd,shell=True,timeout=timeout,
            stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            stdin=subprocess.PIPE if stdin else None,
            input=stdin.encode() if stdin else None,
            env=env)
        out=proc.stdout.decode("utf-8",errors="replace")
        if outfile and out.strip():
            Path(outfile).parent.mkdir(parents=True,exist_ok=True)
            with open(outfile,"a",encoding="utf-8") as f: f.write(out)
        return proc.returncode==0,out
    except subprocess.TimeoutExpired: lw(f"Timeout: {cmd[:60]}"); return False,""
    except Exception as e: return False,str(e)

def run_parallel(cmds:List[Tuple[str,str,int]],workers:int=5)->List[bool]:
    results=[False]*len(cmds); sem=threading.Semaphore(workers)
    def worker(i,cmd,out,t):
        with sem: ok,_=run(cmd,out,t); results[i]=ok
    threads=[threading.Thread(target=worker,args=(i,c,o,t),daemon=True)
             for i,(c,o,t) in enumerate(cmds)]
    for t in threads: t.start()
    for t in threads: t.join()
    return results

def clines(path)->int:
    try:
        with open(path,errors="replace") as f:
            return sum(1 for l in f if l.strip())
    except: return 0

def dedup(path):
    try:
        p2=Path(path)
        if not p2.exists(): return
        lines=sorted(set(l.strip() for l in p2.read_text(errors="replace").splitlines() if l.strip()))
        p2.write_text("\n".join(lines)+"\n")
    except: pass

# ══════════════════════════════════════════════════════
#  OUTPUT MANAGER — Auto-generate all report formats
# ══════════════════════════════════════════════════════
class OutputManager:
    def __init__(self,outdir:Path,db:DB,sid:int,domain:str):
        self.outdir=outdir; self.db=db; self.sid=sid; self.domain=domain

    def generate_all(self, start_time:float):
        """Generate HTML + JSON + Markdown + CSV reports"""
        lsec("GENERATING ALL REPORTS","📊")
        elapsed=time.time()-start_time
        stats=self.db.stats(self.sid)
        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sp=Spin("Generating HTML report","cyber",A.CYN); sp.start()
        self._html(stats,ts,elapsed); sp.stop(True)

        sp=Spin("Generating JSON report","dots",A.GRN); sp.start()
        self._json(stats,ts,elapsed); sp.stop(True)

        sp=Spin("Generating Markdown report","arc",A.YEL); sp.start()
        self._markdown(stats,ts,elapsed); sp.stop(True)

        sp=Spin("Generating CSV findings","bounce",A.ORG); sp.start()
        self._csv(); sp.stop(True)

        sp=Spin("Generating findings summary","pulse",A.MAG); sp.start()
        self._findings_txt(); sp.stop(True)

        lok("All reports generated!")

    def _json(self, stats, ts, elapsed):
        c=self.db.conn.cursor()
        findings=c.execute(
            "SELECT vtype,severity,url,title,tool,ts FROM findings WHERE sid=? ORDER BY severity",
            (self.sid,)).fetchall()
        subs=c.execute(
            "SELECT host,ip,alive,code,title,tech FROM subdomains WHERE sid=?",
            (self.sid,)).fetchall()
        ports=c.execute(
            "SELECT host,port,service,version FROM ports WHERE sid=?",
            (self.sid,)).fetchall()
        data={
            "scan":{"domain":self.domain,"timestamp":ts,
                    "duration_seconds":int(elapsed),"stats":stats},
            "findings":[{"type":r[0],"severity":r[1],"url":r[2],
                         "title":r[3],"tool":r[4],"ts":r[5]} for r in findings],
            "subdomains":[{"host":r[0],"ip":r[1],"alive":bool(r[2]),
                          "status_code":r[3],"title":r[4],"tech":r[5]} for r in subs],
            "ports":[{"host":r[0],"port":r[1],"service":r[2],"version":r[3]} for r in ports],
        }
        (self.outdir/"report.json").write_text(json.dumps(data,indent=2,ensure_ascii=False))

    def _csv(self):
        c=self.db.conn.cursor()
        rows=c.execute(
            "SELECT vtype,severity,url,title,tool,ts FROM findings WHERE sid=?",
            (self.sid,)).fetchall()
        with open(self.outdir/"findings.csv","w",newline="",encoding="utf-8") as f:
            w=csv.writer(f)
            w.writerow(["Type","Severity","URL","Title","Tool","Timestamp"])
            w.writerows(rows)

    def _findings_txt(self):
        c=self.db.conn.cursor()
        out=[]
        out.append(f"MRX FINDINGS REPORT — {self.domain}")
        out.append(f"Generated: {datetime.now()}\n")
        for sev in ["critical","high","medium","low","info"]:
            rows=c.execute(
                "SELECT vtype,url,title,tool FROM findings WHERE sid=? AND severity=?",
                (self.sid,sev)).fetchall()
            if not rows: continue
            out.append(f"\n{'═'*60}")
            out.append(f"[{sev.upper()}] — {len(rows)} findings")
            out.append("═"*60)
            for vtype,url,title,tool in rows:
                out.append(f"  Type:  {vtype}")
                out.append(f"  URL:   {url}")
                out.append(f"  Title: {title}")
                out.append(f"  Tool:  {tool}")
                out.append("")
        (self.outdir/"findings.txt").write_text("\n".join(out))

    def _markdown(self, stats, ts, elapsed):
        c=self.db.conn.cursor()
        md=[]
        md.append(f"# MRX Scan Report — `{self.domain}`\n")
        md.append(f"> **Date:** {ts}  ")
        md.append(f"> **Duration:** {int(elapsed//60)}m {int(elapsed%60)}s\n")
        md.append("## Summary\n")
        md.append("| Metric | Count |")
        md.append("|--------|-------|")
        for k,v in stats.items():
            md.append(f"| {k.title()} | {v} |")
        md.append("\n## Findings\n")
        for sev in ["critical","high","medium","low"]:
            rows=c.execute(
                "SELECT vtype,url,title,tool FROM findings WHERE sid=? AND severity=?",
                (self.sid,sev)).fetchall()
            if not rows: continue
            emoji=SEV_IC.get(sev,"•")
            md.append(f"### {emoji} {sev.upper()} ({len(rows)})\n")
            md.append("| Type | URL | Tool |")
            md.append("|------|-----|------|")
            for vtype,url,title,tool in rows[:30]:
                md.append(f"| {vtype} | `{url[:60]}` | {tool} |")
            md.append("")
        md.append("\n## Subdomains\n")
        subs=c.execute(
            "SELECT host,code,title,tech FROM subdomains WHERE sid=? AND alive=1 LIMIT 50",
            (self.sid,)).fetchall()
        if subs:
            md.append("| Host | Code | Title | Tech |")
            md.append("|------|------|-------|------|")
            for host,code,title,tech in subs:
                md.append(f"| `{host}` | {code} | {title[:40]} | {tech[:40]} |")
        (self.outdir/"report.md").write_text("\n".join(md))

    def _html(self, stats, ts, elapsed):
        c=self.db.conn.cursor()
        findings=c.execute(
            "SELECT vtype,severity,url,title,tool,ts FROM findings WHERE sid=? ORDER BY CASE severity WHEN 'critical' THEN 1 WHEN 'high' THEN 2 WHEN 'medium' THEN 3 WHEN 'low' THEN 4 ELSE 5 END",
            (self.sid,)).fetchall()
        subs=c.execute(
            "SELECT host,ip,alive,code,title,tech FROM subdomains WHERE sid=? ORDER BY alive DESC",
            (self.sid,)).fetchall()[:100]

        sev_colors={"critical":"#ff3333","high":"#ff6633","medium":"#ffaa00",
                    "low":"#ffdd00","info":"#4499ff"}

        findings_rows=""
        for vtype,sev,url,title,tool,fts in findings:
            clr=sev_colors.get(sev,"#888")
            findings_rows+=f"""
            <tr>
              <td><span style="color:{clr};font-weight:600">{sev.upper()}</span></td>
              <td><code style="color:#4fc3f7">{vtype}</code></td>
              <td style="word-break:break-all;max-width:300px"><a href="{url}" target="_blank">{url[:80]}</a></td>
              <td>{title[:60]}</td>
              <td><span class="badge">{tool}</span></td>
            </tr>"""

        subs_rows=""
        for host,ip,alive,code,title,tech in subs:
            alv_c="#4caf50" if alive else "#666"
            code_c="#4caf50" if str(code).startswith("2") else "#ff9800" if str(code).startswith("3") else "#f44336" if str(code).startswith("4") else "#888"
            subs_rows+=f"""
            <tr>
              <td><span style="color:{alv_c}">{'● LIVE' if alive else '○ dead'}</span></td>
              <td><a href="https://{host}" target="_blank">{host}</a></td>
              <td style="color:{code_c}">{code or '-'}</td>
              <td>{ip}</td>
              <td style="color:#888;font-size:12px">{tech[:60]}</td>
            </tr>"""

        stat_cards=""
        stat_defs=[
            ("subdomains",stats['subs'],"#4fc3f7","🌐"),
            ("live hosts", stats['alive'],"#4caf50","✅"),
            ("open ports", stats['ports'],"#ff9800","🔌"),
            ("URLs found", stats['urls'],"#ab47bc","🔗"),
            ("findings",   stats['finds'],"#ff6f00","🔍"),
            ("critical",   stats['crit'],"#f44336","💀"),
            ("high",       stats['high'],"#ff5722","🔥"),
            ("dirs found", stats['dirs'],"#7e57c2","📂"),
        ]
        for lbl,val,clr,icon in stat_defs:
            stat_cards+=f"""
            <div class="stat-card" style="border-top:3px solid {clr}">
              <div class="stat-icon">{icon}</div>
              <div class="stat-val" style="color:{clr}">{val}</div>
              <div class="stat-lbl">{lbl}</div>
            </div>"""

        html=f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MRX Report — {self.domain}</title>
<style>
:root{{--bg:#0a0a0f;--bg2:#0f0f1a;--bg3:#141428;--border:#1e1e3a;
      --text:#e0e0ff;--dim:#666;--cyan:#4fc3f7;--green:#4caf50;}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:var(--bg);color:var(--text);font-family:'Segoe UI',monospace;font-size:14px;line-height:1.6}}
.hero{{background:linear-gradient(135deg,#0a0a2e 0%,#0d0d1f 50%,#0a1628 100%);
       padding:60px 40px;text-align:center;border-bottom:1px solid var(--border);position:relative;overflow:hidden}}
.hero::before{{content:'';position:absolute;inset:0;background:
  radial-gradient(circle at 20% 50%,rgba(79,195,247,0.05) 0%,transparent 60%),
  radial-gradient(circle at 80% 50%,rgba(156,39,176,0.05) 0%,transparent 60%);}}
.hero h1{{font-size:3em;font-weight:800;letter-spacing:4px;
          background:linear-gradient(90deg,#4fc3f7,#ab47bc,#ff6f00);
          -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}}
.hero .sub{{color:#888;margin-top:8px;font-size:1.1em}}
.hero .meta{{margin-top:20px;color:#555;font-size:0.9em}}
.container{{max-width:1400px;margin:0 auto;padding:30px 20px}}
.stats-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin:30px 0}}
.stat-card{{background:var(--bg2);border:1px solid var(--border);border-radius:12px;
            padding:20px;text-align:center;transition:transform .2s}}
.stat-card:hover{{transform:translateY(-2px)}}
.stat-icon{{font-size:1.8em;margin-bottom:8px}}
.stat-val{{font-size:2em;font-weight:700;margin-bottom:4px}}
.stat-lbl{{color:var(--dim);font-size:0.85em;text-transform:uppercase;letter-spacing:1px}}
.section{{background:var(--bg2);border:1px solid var(--border);border-radius:12px;
          margin:20px 0;overflow:hidden}}
.section-header{{background:var(--bg3);padding:16px 24px;border-bottom:1px solid var(--border);
                  display:flex;align-items:center;gap:10px}}
.section-header h2{{font-size:1.1em;letter-spacing:2px;color:var(--cyan)}}
.section-content{{padding:0}}
table{{width:100%;border-collapse:collapse}}
th{{background:var(--bg3);padding:12px 16px;text-align:left;
    color:#888;font-size:0.8em;text-transform:uppercase;letter-spacing:1px;
    border-bottom:1px solid var(--border)}}
td{{padding:10px 16px;border-bottom:1px solid rgba(255,255,255,0.04);
    font-size:0.9em;vertical-align:middle}}
tr:hover td{{background:rgba(255,255,255,0.02)}}
a{{color:var(--cyan);text-decoration:none}}
a:hover{{text-decoration:underline}}
code{{background:#1a1a2e;padding:2px 6px;border-radius:4px;font-size:0.9em}}
.badge{{background:#1a1a3e;border:1px solid #2a2a5e;padding:2px 8px;
        border-radius:20px;font-size:0.8em;color:#888}}
.footer{{text-align:center;padding:40px;color:#333;font-size:0.8em}}
@keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.5}}}}
.live{{animation:pulse 2s infinite}}
</style>
</head>
<body>
<div class="hero">
  <h1>MRX</h1>
  <div class="sub">Advanced Bug Bounty Framework v4.0</div>
  <div class="meta">
    Target: <strong style="color:var(--cyan)">{self.domain}</strong> &nbsp;|&nbsp;
    {ts} &nbsp;|&nbsp;
    Duration: {int(elapsed//60)}m {int(elapsed%60)}s
  </div>
</div>
<div class="container">
  <div class="stats-grid">{stat_cards}</div>

  <div class="section">
    <div class="section-header"><span>⚠</span><h2>FINDINGS ({len(findings)})</h2></div>
    <div class="section-content">
      <table><thead><tr>
        <th>Severity</th><th>Type</th><th>URL</th><th>Title</th><th>Tool</th>
      </tr></thead><tbody>{findings_rows or '<tr><td colspan="5" style="text-align:center;color:#444;padding:30px">No findings</td></tr>'}
      </tbody></table>
    </div>
  </div>

  <div class="section">
    <div class="section-header"><span>🌐</span><h2>SUBDOMAINS ({len(subs)})</h2></div>
    <div class="section-content">
      <table><thead><tr>
        <th>Status</th><th>Host</th><th>Code</th><th>IP</th><th>Tech Stack</th>
      </tr></thead><tbody>{subs_rows or '<tr><td colspan="5" style="text-align:center;color:#444;padding:30px">No data</td></tr>'}
      </tbody></table>
    </div>
  </div>
</div>
<div class="footer">Generated by MRX Bug Bounty Framework v4.0 · {ts}</div>
</body></html>"""
        (self.outdir/"report.html").write_text(html)

# ══════════════════════════════════════════════════════
#  MRX WORKFLOW
# ══════════════════════════════════════════════════════
class MRX:
    def __init__(self,domain,outdir,db,sid,cfg,proxy_mgr):
        self.domain=domain; self.outdir=outdir; self.db=db
        self.sid=sid; self.cfg=cfg; self.pm=proxy_mgr
        self.dash=None
        self.subs_file=None; self.live_file=None; self.urls_file=None

    def _p(self,n): return self.outdir/n
    def _penv(self): return self.pm.get_env() if self.pm else {}
    def _pcurl(self): return self.pm.get_curl_flag() if self.pm else ""

    def start_dash(self):
        self.dash=Dashboard(self.db,self.sid,self.domain); self.dash.start()

    def stop_dash(self):
        if self.dash: self.dash.stop(); self.dash=None

    def _dash_step(self,s):
        if self.dash: self.dash.set_step(s)

    def _dash_event(self,m,sev="info"):
        if self.dash: self.dash.add_event(m,sev)

    # ── M01: Subdomain Enum ──────────────────────────
    def m01_subdomains(self):
        lstep(1,"Subdomain Enumeration"); self._dash_step("Subdomains")
        raw=self._p("subs_raw.txt"); final=self._p("subs.txt")
        d=self.domain; penv=self._penv()

        cmds=[]
        if avail("subfinder"):
            cmds.append((f"subfinder -d {d} -silent -all -recursive",str(raw),90))
        if avail("assetfinder"):
            cmds.append((f"assetfinder --subs-only {d}",str(raw),60))
        if cmds:
            sp=Spin(f"Running {len(cmds)} enumerators in parallel","bounce",A.CYN)
            sp.start(); run_parallel(cmds,workers=len(cmds)); sp.stop(True)

        if avail("amass"):
            sp=Spin("amass passive OSINT","dots",A.BLU); sp.start()
            run(f"amass enum -passive -d {d} -o {self.outdir}/subs_amass.txt",timeout=200,proxy_env=penv)
            run(f"cat {self.outdir}/subs_amass.txt >> {raw} 2>/dev/null")
            sp.stop(True)

        if avail("dnsx"):
            dns_wl=wl("dns")
            if dns_wl:
                sp=Spin("dnsx DNS bruteforce","arc",A.CYN); sp.start()
                run(f"dnsx -d {d} -w {dns_wl} -silent -o {self.outdir}/subs_dns.txt",timeout=120)
                run(f"cat {self.outdir}/subs_dns.txt >> {raw} 2>/dev/null")
                sp.stop(True)

        # Certificate transparency via crt.sh
        sp=Spin("crt.sh certificate transparency","cyber",A.PURP); sp.start()
        try:
            ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
            url=f"https://crt.sh/?q=%.{d}&output=json"
            req=Request(url,headers={"User-Agent":"mrx/4.0"},method="GET")
            with urlopen(req,timeout=20,context=ctx) as r:
                data=json.loads(r.read())
                ct_subs=set()
                for entry in data:
                    for name in entry.get("name_value","").splitlines():
                        name=name.strip().lstrip("*.")
                        if name.endswith(f".{d}") or name==d:
                            ct_subs.add(name)
                if ct_subs:
                    with open(raw,"a") as f:
                        f.write("\n".join(ct_subs)+"\n")
            sp.stop(True)
        except: sp.stop(False)

        if raw.exists():
            run(f"sort -u {raw} > {final}")
        elif not final.exists():
            final.write_text(f"{d}\n")

        total=clines(final)
        try:
            with open(final) as f:
                for line in f:
                    sub=line.strip()
                    if sub: self.db.add_sub(self.sid,sub)
        except: pass

        lfound(f"Discovered {p(A.YEL+A.BOLD,str(total))} subdomains","info")
        self._dash_event(f"{total} subdomains found","info")
        self.subs_file=final; return final

    # ── M02: Live Hosts ──────────────────────────────
    def m02_live(self):
        lstep(2,"Live Host Detection"); self._dash_step("Live Hosts")
        if not self.subs_file or not self.subs_file.exists():
            lw("No subs file"); return None
        live=self._p("live.txt"); live_json=self._p("live.json")
        if not avail("httpx"): lw("httpx missing"); return None

        sp=Spin("httpx probing all hosts","bounce",A.GRN); sp.start()
        run(f"httpx -l {self.subs_file} -silent -status-code -title "
            f"-tech-detect -content-length -follow-redirects "
            f"-threads 80 -timeout 10 -o {live_json} -json",timeout=400)
        sp.stop(True)

        if live_json.exists():
            try:
                with open(live_json) as f:
                    for line in f:
                        line=line.strip()
                        if not line: continue
                        try:
                            d=json.loads(line); url=d.get("url","")
                            with open(live,"a") as lf: lf.write(url+"\n")
                            host=urlparse(url).netloc or url
                            self.db.add_sub(self.sid,host,alive=1,
                                code=d.get("status_code",0),
                                title=d.get("title","")[:100],
                                tech=",".join(d.get("tech",[]))[:200])
                        except: pass
            except: pass
        else:
            run(f"httpx -l {self.subs_file} -silent -o {live} -threads 80",timeout=400)

        dedup(live); total=clines(live)
        lfound(f"{p(A.YEL+A.BOLD,str(total))} live hosts","info")
        self._dash_event(f"{total} live hosts","info")
        self.live_file=live; return live

    # ── M03: Port Scan ────────────────────────────────
    def m03_ports(self):
        lstep(3,"Port Scanning"); self._dash_step("Port Scan")
        out=self._p("ports.txt"); d=self.domain

        if avail("naabu"):
            sp=Spin("naabu fast port discovery","scan",A.ORG); sp.start()
            target=f"-list {self.live_file}" if self.live_file else f"-host {d}"
            ok,output=run(f"naabu {target} -top-ports 1000 -silent -c 50 -o {out}",timeout=300)
            sp.stop(ok)
            for line in output.splitlines():
                if ":" in line:
                    parts=line.strip().split(":")
                    if len(parts)==2 and parts[1].isdigit():
                        self.db.add_port(self.sid,parts[0],int(parts[1]))

        if avail("nmap"):
            sp=Spin("nmap service/version detection","dots",A.BLU); sp.start()
            iL=f"-iL {self.live_file}" if self.live_file and self.live_file.exists() else ""
            run(f"nmap -sV -sC --open -T4 {iL} "
                f"--script=http-title,ssl-cert,http-headers "
                f"-oN {self._p('nmap.txt')} -oX {self._p('nmap.xml')} {d}",timeout=400)
            sp.stop(True)

        total=clines(out)
        lfound(f"{p(A.YEL+A.BOLD,str(total))} open ports","info")
        self._dash_event(f"{total} ports open","info"); return out

    # ── M04: Fuzzing ──────────────────────────────────
    def m04_fuzz(self):
        lstep(4,"Directory & File Fuzzing"); self._dash_step("Fuzzing")
        if not avail("ffuf"): lw("ffuf missing"); return None
        wl_c=wl("common"); wl_s=wl("large")
        if not wl_c: lw("No wordlists"); return None
        dirs_out=self._p("dirs.txt")
        pcurl=self._pcurl()

        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:25]
        else: targets=[f"https://{self.domain}",f"http://{self.domain}"]

        for i,target in enumerate(targets):
            pbar(i+1,len(targets),f"Fuzzing {target[:45]}")
            proxy_flag=f"-x http://{self.pm.next()}" if self.pm and self.pm.proxies else ""
            run(f"ffuf -u {target}/FUZZ -w {wl_c} "
                f"-mc 200,201,204,301,302,307,401,403,405 "
                f"-c -t 60 -timeout 8 {proxy_flag} "
                f"-of csv -o /tmp/mrx_ffuf.csv 2>/dev/null",timeout=180)
            try:
                with open("/tmp/mrx_ffuf.csv") as f:
                    for line in f:
                        if line.startswith("FUZZ"): continue
                        parts=line.strip().split(",")
                        if len(parts)>=4 and parts[0]:
                            url=f"{target}/{parts[0]}"
                            code=int(parts[3]) if parts[3].isdigit() else 0
                            size=int(parts[2]) if parts[2].isdigit() else 0
                            with open(dirs_out,"a") as df: df.write(url+"\n")
                            self.db.add_dir(self.sid,url,code,size)
            except: pass

        print()
        dedup(dirs_out); total=clines(dirs_out)
        lfound(f"{p(A.YEL+A.BOLD,str(total))} paths discovered","info")
        self._dash_event(f"{total} dirs found","info")

        if avail("feroxbuster") and self.cfg.get("deep"):
            sp=Spin("feroxbuster recursive scan","bounce",A.MAG); sp.start()
            run(f"feroxbuster -u https://{self.domain} -w {wl_s or wl_c} "
                f"--silent --depth 3 -t 50 -o {self._p('ferox.txt')}",timeout=300)
            sp.stop(True)
        return dirs_out

    # ── M05: URL Collection ───────────────────────────
    def m05_urls(self):
        lstep(5,"URL & Parameter Collection"); self._dash_step("URL Collection")
        combined=self._p("all_urls.txt"); d=self.domain
        penv=self._penv()

        cmds=[]
        if avail("gau"):
            cmds.append((f"gau {d} --threads 10 --timeout 60 --subs "
                         f"--blacklist png,jpg,gif,woff,ttf",
                         str(self._p("urls_gau.txt")),120))
        if avail("waybackurls"):
            cmds.append((f"echo {d} | waybackurls",
                         str(self._p("urls_wb.txt")),90))
        if avail("hakrawler"):
            cmds.append((f"echo https://{d} | hakrawler -depth 3 -subs",
                         str(self._p("urls_hak.txt")),90))

        if cmds:
            sp=Spin(f"Collecting URLs from {len(cmds)} sources in parallel","bounce",A.CYN)
            sp.start(); run_parallel(cmds,workers=3); sp.stop(True)

        if avail("katana"):
            sp=Spin("katana active crawling","cyber",A.PURP); sp.start()
            proxy_flag=f"-proxy http://{self.pm.next()}" if self.pm and self.pm.proxies else ""
            run(f"katana -u https://{d} -silent -depth 3 -jc {proxy_flag} "
                f"-kf all -o {self._p('urls_katana.txt')}",timeout=200)
            sp.stop(True)

        run(f"cat {self.outdir}/urls_*.txt 2>/dev/null | sort -u > {combined}")
        total=clines(combined)
        lfound(f"{p(A.YEL+A.BOLD,str(total))} URLs collected","info")

        try:
            with open(combined) as f:
                for i,line in enumerate(f):
                    if i>10000: break
                    url=line.strip()
                    if url: self.db.add_url(self.sid,url,src="passive")
        except: pass

        # gf pattern filtering
        if avail("gf") and total>0:
            sp=Spin("gf filtering vulnerable parameters","scan",A.YEL); sp.start()
            for gft in ["xss","sqli","ssrf","redirect","lfi","rce","idor","ssti"]:
                out_p=self._p(f"params_{gft}.txt")
                run(f"cat {combined} | gf {gft} > {out_p} 2>/dev/null",timeout=30)
                n=clines(out_p)
                if n>0: self._dash_event(f"{n} {gft.upper()} params","medium")
            sp.stop(True)
        else:
            run(f"grep '=' {combined} | head -500 > {self._p('params_all.txt')} 2>/dev/null")

        if avail("qsreplace") and combined.exists():
            run(f"cat {combined} | grep '=' | qsreplace 'MRXSSRF' "
                f"> {self._p('ssrf_payloads.txt')} 2>/dev/null")
            run(f"cat {combined} | grep '=' | qsreplace 'https://evil.com' "
                f"> {self._p('redirect_payloads.txt')} 2>/dev/null")

        self.urls_file=combined; return combined

    # ── M06: JS Analysis ──────────────────────────────
    def m06_js(self):
        lstep(6,"JavaScript Analysis & Secret Scanning"); self._dash_step("JS Analysis")
        js_out=self._p("js_files.txt"); secrets=self._p("js_secrets.txt")

        if self.urls_file and self.urls_file.exists():
            run(f"grep -iE '\\.js(\\?|$)' {self.urls_file} | sort -u > {js_out}")

        js_count=clines(js_out)
        li(f"Found {p(A.YEL,str(js_count))} JS files to analyze")

        SECRET_PATTERNS={
            "AWS_KEY":       r'AKIA[0-9A-Z]{16}',
            "AWS_SECRET":    r'(?i)aws[_\-\s]?secret[_\-\s]?(?:access[_\-\s]?)?key["\s]*[=:]["\s]*([A-Za-z0-9/+=]{40})',
            "Google_API":    r'AIza[0-9A-Za-z\-_]{35}',
            "JWT":           r'eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+',
            "Private_Key":   r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
            "Slack_Token":   r'xox[baprs]-[0-9A-Za-z]{10,48}',
            "GitHub_Token":  r'ghp_[0-9A-Za-z]{36}',
            "Stripe_Key":    r'(?:sk|pk)_(?:live|test)_[0-9A-Za-z]{24,}',
            "SendGrid":      r'SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}',
            "Firebase":      r'https://[a-z0-9-]+\.firebaseio\.com',
            "API_Key":       r'(?i)(?:api[_\-]?key|apikey)["\s]*[=:]["\s]*["\']([a-zA-Z0-9_\-]{16,})["\']',
            "Password":      r'(?i)(?:password|passwd|pwd)["\s]*[=:]["\s]*["\']([^"\']{8,})["\']',
            "Authorization": r'(?i)authorization["\s]*[=:]["\s]*["\'](?:Bearer |Basic )?([A-Za-z0-9+/=_\-\.]{20,})["\']',
        }

        secrets_found=0
        if js_out.exists() and js_count>0:
            sp=Spin(f"Scanning {js_count} JS files for secrets","pulse",A.RED); sp.start()
            pcurl=self._pcurl()
            try:
                with open(js_out) as f:
                    js_urls=[l.strip() for l in f if l.strip()][:100]
                for js_url in js_urls:
                    _,content=run(f"curl -sk --max-time 8 {pcurl} '{js_url}'",timeout=12)
                    if not content: continue
                    for sec_name,pattern in SECRET_PATTERNS.items():
                        matches=re.findall(pattern,content)
                        if matches:
                            with open(secrets,"a") as sf:
                                sf.write(f"[{sec_name}] {js_url}\n{str(matches[0])[:200]}\n\n")
                            self.db.add_finding(self.sid,type=f"Secret: {sec_name}",
                                severity="high",url=js_url,
                                title=f"{sec_name} exposed in JS",tool="mrx-secret-scan")
                            secrets_found+=1
                            self._dash_event(f"SECRET: {sec_name} in JS","high")
            except: pass
            sp.stop(True)

        if secrets_found:
            lfound(f"🔑 {secrets_found} secrets found → {secrets}","high")

    # ── M07: Nuclei ────────────────────────────────────
    def m07_nuclei(self):
        lstep(7,"Nuclei Vulnerability Scanner"); self._dash_step("Nuclei")
        if not avail("nuclei"): lw("nuclei missing"); return

        sp=Spin("Updating nuclei templates","arc",A.GRN); sp.start()
        run("nuclei -update-templates -silent",timeout=90); sp.stop(True)

        target=(f"-l {self.live_file}" if self.live_file and self.live_file.exists()
                else f"-u https://{self.domain}")
        proxy_flag=f"-proxy http://{self.pm.next()}" if self.pm and self.pm.proxies else ""

        profiles=[
            ("cves",              A.RED,   "critical,high",      "Known CVEs",         280),
            ("exposures",         A.ORG,   "medium,high",        "Exposed Files",      220),
            ("misconfigurations", A.YEL,   "medium,high",        "Misconfigs",         220),
            ("vulnerabilities",   A.MAG,   "medium,high,critical","Web Vulns",         280),
            ("technologies",      A.BLU,   "info",               "Tech Stack",         150),
            ("default-logins",    A.LRED,  "medium,high",        "Default Creds",      200),
            ("takeovers",         A.RED,   "high,critical",      "Takeovers",          200),
            ("network",           A.CYN,   "medium,high",        "Network Issues",     200),
            ("file",              A.PURP,  "medium,high",        "File Inclusion",     200),
        ]

        total=0
        for tmpl,color,sev,label,timeout in profiles:
            out_f=self._p(f"nuclei_{tmpl}.txt")
            sp=Spin(f"  {label}","dots",color); sp.start()
            run(f"nuclei {target} -t {tmpl}/ -silent "
                f"-severity {sev} -rate-limit 60 -bulk-size 30 "
                f"-timeout 10 {proxy_flag} -o {out_f} 2>/dev/null",timeout=timeout)
            sp.stop(True)
            n=clines(out_f)
            if n:
                total+=n
                lfound(f"  {p(color,label)}: {p(A.YEL+A.BOLD,str(n))}",
                       "high" if sev.startswith("critical") else "medium")
                self._dash_event(f"Nuclei {label}: {n} hits","high")
                try:
                    with open(out_f) as f:
                        for line in f:
                            line=line.strip()
                            if not line: continue
                            m=re.match(r'\[(.+?)\]\s*\[(.+?)\]\s*(.+)',line)
                            if m:
                                self.db.add_finding(self.sid,type=m.group(1),
                                    severity=m.group(2).lower().split(",")[0],
                                    url=m.group(3),title=m.group(1),tool="nuclei")
                except: pass

        run(f"cat {self.outdir}/nuclei_*.txt 2>/dev/null | sort -u > {self._p('nuclei_all.txt')}")
        if total: lfound(f"Total nuclei: {p(A.RED+A.BOLD,str(total))} findings","critical")

    # ── M08: XSS ───────────────────────────────────────
    def m08_xss(self):
        lstep(8,"XSS Scanning"); self._dash_step("XSS")
        xss_out=self._p("xss_results.txt")
        params=self._p("params_xss.txt")
        if not avail("dalfox"): lw("dalfox missing"); return
        if not params.exists():
            if self.urls_file:
                run(f"grep '=' {self.urls_file} | head -300 > {params} 2>/dev/null")
        n=clines(params)
        if n==0: lw("No XSS candidates"); return
        li(f"Testing {p(A.YEL,str(n))} URLs for XSS")
        proxy_flag=f"--proxy http://{self.pm.next()}" if self.pm and self.pm.proxies else ""
        sp=Spin("dalfox DOM/Reflected XSS","bounce",A.PINK); sp.start()
        ok,_=run(f"dalfox file {params} --silence "
                 f"--timeout 10 --worker 40 {proxy_flag} "
                 f"--output {xss_out} --skip-bav 2>/dev/null",timeout=400)
        sp.stop(ok)
        nf=clines(xss_out)
        if nf:
            lfound(f"XSS: {p(A.RED+A.BOLD,str(nf))} findings","high")
            self._dash_event(f"{nf} XSS found","high")
            try:
                with open(xss_out) as f:
                    for line in f:
                        url=line.strip()
                        if url:
                            self.db.add_finding(self.sid,type="XSS",severity="high",
                                url=url,title="Cross-Site Scripting",tool="dalfox")
            except: pass

    # ── M09: SQLi ──────────────────────────────────────
    def m09_sqli(self):
        lstep(9,"SQL Injection"); self._dash_step("SQLi")
        sqli_dir=self._p("sqlmap_results"); sqli_dir.mkdir(exist_ok=True)
        params=self._p("params_sqli.txt")
        if not avail("sqlmap"): lw("sqlmap missing"); return
        if not params.exists() or clines(params)==0:
            if self.urls_file:
                run(f"grep -E '(id|page|num|item|pid)=' {self.urls_file} "
                    f"| head -50 > {params} 2>/dev/null")
        n=clines(params)
        if n==0: lw("No SQLi candidates"); return
        li(f"Testing {p(A.YEL,str(min(n,50)))} URLs for SQLi")
        proxy_flag=f"--proxy=http://{self.pm.next()}" if self.pm and self.pm.proxies else ""
        sp=Spin("sqlmap injection detection","scan",A.ORG); sp.start()
        run(f"sqlmap -m {params} --batch --level=2 --risk=2 "
            f"--threads=5 --timeout=15 --random-agent "
            f"{proxy_flag} --output-dir={sqli_dir} -q 2>/dev/null",timeout=500)
        sp.stop(True); li(f"SQLmap results → {p(A.GRY,str(sqli_dir))}")

    # ── M10: Takeover ──────────────────────────────────
    def m10_takeover(self):
        lstep(10,"Subdomain Takeover"); self._dash_step("Takeover")
        out=self._p("takeover.txt")
        if not avail("subzy"): lw("subzy missing"); return
        if not self.subs_file or not self.subs_file.exists(): return
        sp=Spin("subzy takeover detection","bounce",A.RED); sp.start()
        ok,output=run(f"subzy run --targets {self.subs_file} "
                      f"--concurrency 100 --hide-fails --output {out}",timeout=300)
        sp.stop(ok); n=clines(out)
        if n:
            lfound(f"Takeovers: {p(A.RED+A.BOLD,str(n))}","critical")
            self._dash_event(f"{n} takeover candidates","critical")

    # ── M11: CORS ──────────────────────────────────────
    def m11_cors(self):
        lstep(11,"CORS Misconfiguration"); self._dash_step("CORS")
        cors_out=self._p("cors_results.txt"); found=0
        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:20]
        else: targets=[f"https://{self.domain}"]

        sp=Spin(f"Testing {len(targets)} targets for CORS","arc",A.CYN); sp.start()
        pcurl=self._pcurl()
        for target in targets:
            _,out=run(f"curl -sk -I '{target}' {pcurl} "
                      f"-H 'Origin: https://evil.com' --max-time 8 "
                      f"| grep -i 'access-control'",timeout=12)
            if out and ("evil.com" in out.lower() or "access-control-allow-origin: *" in out.lower()):
                with open(cors_out,"a") as f:
                    f.write(f"[CORS VULN] {target}\n{out}\n\n")
                self.db.add_finding(self.sid,type="CORS",severity="medium",
                    url=target,title="CORS Misconfiguration",tool="mrx-cors")
                found+=1; self._dash_event(f"CORS: {target[:40]}","medium")
        sp.stop(True)
        if found: lfound(f"CORS issues: {p(A.YEL+A.BOLD,str(found))}","medium")

    # ── M12: Nikto ─────────────────────────────────────
    def m12_nikto(self):
        lstep(12,"Nikto Web Server Scan"); self._dash_step("Nikto")
        nikto_out=self._p("nikto.txt")
        if not avail("nikto"): lw("nikto missing"); return
        targets=[f"https://{self.domain}"]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f:
                targets=[l.strip() for l in f][:5]
        for target in targets:
            sp=Spin(f"nikto → {target[:50]}","arc",A.YEL); sp.start()
            ok,output=run(f"nikto -h {target} -output {nikto_out} "
                          f"-Format txt -timeout 15 -nointeractive -Tuning 13457 2>/dev/null",
                          timeout=300)
            sp.stop(ok)
            for line in output.splitlines():
                if "+ " in line and len(line)>20:
                    self.db.add_finding(self.sid,type="Web Server",severity="medium",
                        url=target,title=line[:120],tool="nikto")


    # ── M13: SSL/TLS Audit ────────────────────────────
    def m13_ssl(self):
        lstep(13,"SSL/TLS Security Audit"); self._dash_step("SSL/TLS")
        out=self._p("ssl_results.txt"); d=self.domain
        # Built-in SSL check via Python ssl module
        sp=Spin("Checking SSL/TLS configuration","arc",A.CYN); sp.start()
        issues=[]
        try:
            ctx=ssl.create_default_context()
            with socket.create_connection((d,443),timeout=10) as sock:
                with ctx.wrap_socket(sock,server_hostname=d) as ssock:
                    cert=ssock.getpeercert(); proto=ssock.version()
                    cipher=ssock.cipher()
                    exp=cert.get('notAfter','')
                    subj=dict(x[0] for x in cert.get('subject',()))
                    # Check expiry
                    try:
                        from datetime import timezone
                        exp_dt=datetime.strptime(exp,'%b %d %H:%M:%S %Y %Z')
                        days_left=(exp_dt-datetime.utcnow()).days
                        if days_left<30: issues.append(f"CERT EXPIRES SOON: {days_left} days ({exp})")
                    except: pass
                    # Weak protocols
                    if proto in ('SSLv2','SSLv3','TLSv1','TLSv1.1'):
                        issues.append(f"WEAK PROTOCOL: {proto}")
                    # Weak ciphers
                    if cipher and any(w in str(cipher) for w in ['RC4','DES','NULL','EXPORT','MD5']):
                        issues.append(f"WEAK CIPHER: {cipher[0]}")
                    with open(out,"w") as f:
                        f.write(f"Host: {d}\nProtocol: {proto}\nCipher: {cipher}\n")
                        f.write(f"Subject: {subj}\nExpires: {exp}\n")
                        if issues:
                            f.write("\nISSUES:\n"+"\n".join(issues))
        except ssl.SSLError as e:
            issues.append(f"SSL ERROR: {e}")
            with open(out,"w") as fw: fw.write(str(e))
        except Exception as e:
            with open(out,"w") as fw: fw.write(str(e))
        sp.stop(True)
        if issues:
            for iss in issues:
                lfound(f"SSL: {iss}","medium")
                self.db.add_finding(self.sid,type="SSL/TLS Issue",severity="medium",
                    url=f"https://{d}",title=iss,tool="mrx-ssl")
                self._dash_event(f"SSL issue: {iss[:40]}","medium")
        # testssl if available
        if avail("testssl.sh") or avail("testssl"):
            cmd="testssl.sh" if avail("testssl.sh") else "testssl"
            sp=Spin("testssl.sh — comprehensive SSL audit","scan",A.BLU); sp.start()
            run(f"{cmd} --quiet --color 0 {d} > {self._p('testssl.txt')} 2>&1",timeout=180)
            sp.stop(True)

    # ── M14: DNS Recon ────────────────────────────────
    def m14_dns(self):
        lstep(14,"DNS Reconnaissance"); self._dash_step("DNS Recon")
        out=self._p("dns_recon.txt"); d=self.domain
        sp=Spin("DNS enumeration — all record types","arc",A.CYN); sp.start()
        dns_results=[]
        record_types=["A","AAAA","MX","NS","TXT","SOA","CNAME","CAA","PTR","SRV"]
        for rtype in record_types:
            ok,out_data=run(f"dig +short {rtype} {d} 2>/dev/null",timeout=10)
            if ok and out_data.strip():
                dns_results.append(f"[{rtype}]\n{out_data.strip()}")
        with open(out,"w") as f:
            f.write(f"DNS Recon — {d}\n{'='*50}\n")
            f.write("\n\n".join(dns_results))
        sp.stop(True)
        # Zone transfer attempt
        sp=Spin("DNS zone transfer check (AXFR)","bounce",A.RED); sp.start()
        zt_out=self._p("zone_transfer.txt")
        # Get NS records first
        _,ns_data=run(f"dig +short NS {d} 2>/dev/null",timeout=8)
        for ns in ns_data.splitlines():
            ns=ns.strip().rstrip(".")
            if not ns: continue
            ok,zt=run(f"dig AXFR {d} @{ns} 2>/dev/null",timeout=15)
            if ok and "Transfer failed" not in zt and len(zt)>100:
                with open(zt_out,"a") as f: f.write(f"[ZONE XFER from {ns}]\n{zt}\n")
                self.db.add_finding(self.sid,type="DNS Zone Transfer",severity="high",
                    url=f"dns://{d}",title=f"Zone transfer via {ns}",tool="dig")
                lfound(f"Zone transfer ALLOWED via {ns}!","high")
                self._dash_event(f"ZONE XFER: {ns}","high")
        sp.stop(True)
        # SPF/DMARC check
        _,spf=run(f"dig +short TXT {d} 2>/dev/null | grep spf",timeout=8)
        _,dmarc=run(f"dig +short TXT _dmarc.{d} 2>/dev/null",timeout=8)
        if not spf.strip():
            self.db.add_finding(self.sid,type="Missing SPF",severity="low",
                url=f"dns://{d}",title="No SPF record found",tool="dig")
        if not dmarc.strip():
            self.db.add_finding(self.sid,type="Missing DMARC",severity="low",
                url=f"dns://{d}",title="No DMARC record found",tool="dig")
        li(f"DNS recon saved → {p(A.GRY,str(out))}")

    # ── M15: S3/Cloud Bucket Enum ─────────────────────
    def m15_buckets(self):
        lstep(15,"Cloud Storage & S3 Bucket Enumeration"); self._dash_step("S3 Buckets")
        d=self.domain
        # Extract company name
        company=d.split('.')[0]
        words=company.split('-')+company.split('_')+[company]
        bucket_names=set()
        for w in words:
            for tmpl in ["{w}","{w}-backup","{w}-dev","{w}-prod","{w}-staging",
                          "{w}-static","{w}-assets","{w}-uploads","{w}-files",
                          "{w}-data","{w}-media","{w}-public","dev-{w}","prod-{w}"]:
                bucket_names.add(tmpl.format(w=w))
        out=self._p("buckets.txt"); found=0
        sp=Spin(f"Checking {len(bucket_names)} bucket names","scan",A.GOLD); sp.start()
        pcurl=self._pcurl()
        for bucket in list(bucket_names)[:40]:
            urls=[f"https://{bucket}.s3.amazonaws.com",
                  f"https://storage.googleapis.com/{bucket}",
                  f"https://{bucket}.blob.core.windows.net"]
            for url in urls:
                _,resp=run(f"curl -sk --max-time 6 {pcurl} -o /dev/null "
                           f"-w '%{{http_code}}' '{url}'",timeout=9)
                code=resp.strip()
                if code in ("200","403"):
                    with open(out,"a") as f:
                        f.write(f"[{code}] {url}\n")
                    sev="high" if code=="200" else "medium"
                    self.db.add_finding(self.sid,type="Open Cloud Bucket",
                        severity=sev,url=url,
                        title=f"S3/GCS bucket {'PUBLIC' if code=='200' else 'exists'}",
                        tool="mrx-bucket")
                    self._dash_event(f"BUCKET {code}: {bucket}",sev)
                    found+=1
        sp.stop(True)
        if found: lfound(f"Buckets found: {p(A.YEL+A.BOLD,str(found))}","high")

    # ── M16: WordPress Scan ───────────────────────────
    def m16_wordpress(self):
        lstep(16,"WordPress Detection & Scanning"); self._dash_step("WordPress")
        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:10]
        else: targets=[f"https://{self.domain}"]
        wp_targets=[]; pcurl=self._pcurl()
        sp=Spin("Detecting WordPress installations","arc",A.BLU); sp.start()
        for target in targets:
            _,resp=run(f"curl -sk --max-time 8 {pcurl} '{target}/wp-login.php' "
                       f"-o /dev/null -w '%{{http_code}}'",timeout=12)
            if resp.strip() in ("200","302","301"):
                wp_targets.append(target)
                self.db.add_finding(self.sid,type="WordPress Detected",severity="info",
                    url=target,title="WordPress CMS detected",tool="mrx-wp")
        sp.stop(True)
        if not wp_targets: li("No WordPress sites detected"); return
        li(f"WordPress found on {p(A.YEL,str(len(wp_targets)))} targets")
        if avail("wpscan"):
            for target in wp_targets:
                sp=Spin(f"wpscan → {target[:50]}","bounce",A.ORG); sp.start()
                out=self._p(f"wpscan_{hash(target)%9999}.json")
                run(f"wpscan --url {target} --no-banner --format json "
                    f"-o {out} --enumerate vp,u,tt 2>/dev/null",timeout=300)
                sp.stop(True)
        else:
            # Manual checks
            for target in wp_targets:
                sp=Spin(f"Manual WP checks → {target[:40]}","dots",A.ORG); sp.start()
                checks=[
                    ("/wp-json/wp/v2/users","User enumeration via REST API","medium"),
                    ("/xmlrpc.php","XML-RPC enabled","medium"),
                    ("/wp-content/debug.log","Debug log exposed","high"),
                    ("/?author=1","Author ID enumeration","low"),
                    ("/wp-config.php.bak","WP config backup exposed","critical"),
                ]
                for path,title,sev in checks:
                    _,resp=run(f"curl -sk --max-time 6 {pcurl} "
                               f"'{target}{path}' -o /dev/null -w '%{{http_code}}'",timeout=9)
                    if resp.strip() in ("200","403"):
                        self.db.add_finding(self.sid,type="WordPress Issue",
                            severity=sev,url=f"{target}{path}",title=title,tool="mrx-wp")
                        self._dash_event(f"WP: {title[:40]}",sev)
                sp.stop(True)

    # ── M17: Email Harvesting ─────────────────────────
    def m17_emails(self):
        lstep(17,"Email Harvesting & OSINT"); self._dash_step("Email Harvest")
        d=self.domain; out=self._p("emails.txt"); emails=set()
        sp=Spin("Harvesting emails from multiple sources","cyber",A.MAG); sp.start()
        pcurl=self._pcurl()
        # crt.sh
        try:
            ctx=ssl.create_default_context(); ctx.check_hostname=False
            ctx.verify_mode=ssl.CERT_NONE
            from urllib.request import Request as UReq, urlopen as uopen
            req=UReq(f"https://crt.sh/?q={d}&output=json",
                     headers={"User-Agent":"MRX/4.0"})
            with uopen(req,timeout=15,context=ctx) as r:
                data=json.loads(r.read())
            for entry in data:
                for email in re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.'+
                                       d.replace('.', r'\.')[:50],
                                       str(entry)):
                    emails.add(email.lower())
        except: pass
        # grep from URLs
        if self.urls_file and self.urls_file.exists():
            _,out_data=run(
                f"grep -oiE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+[.][a-zA-Z]{{2,}}' "
                f"{self.urls_file} 2>/dev/null",timeout=20)
            for email in out_data.splitlines():
                if d in email.lower(): emails.add(email.lower().strip())
        sp.stop(True)
        if emails:
            with open(out,"w") as f: f.write("\n".join(sorted(emails)))
            lfound(f"Emails found: {p(A.YEL+A.BOLD,str(len(emails)))}","info")
            for email in list(emails)[:5]:
                li(f"  → {p(A.CYN,email)}")
        else: li("No emails harvested")

    # ── M18: Technology Stack Deep Scan ───────────────
    def m18_tech(self):
        lstep(18,"Technology Stack Analysis"); self._dash_step("Tech Analysis")
        out=self._p("tech_stack.txt"); pcurl=self._pcurl()
        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:15]
        else: targets=[f"https://{self.domain}"]
        sp=Spin("Fingerprinting technology stacks","scan",A.TEAL); sp.start()
        tech_sigs={
            "React":       ["react","__REACT_DEVTOOLS","react-root"],
            "Angular":     ["ng-version","angular.js","AngularJS"],
            "Vue.js":      ["__vue","Vue.js","nuxt"],
            "jQuery":      ["jquery.min.js","jQuery.fn.jquery"],
            "Bootstrap":   ["bootstrap.min.css","bootstrap.min.js"],
            "WordPress":   ["wp-content","wp-includes","WordPress"],
            "Laravel":     ["laravel_session","Laravel"],
            "Django":      ["csrfmiddlewaretoken","django"],
            "Rails":       ["authenticity_token","Ruby on Rails"],
            "Express.js":  ["X-Powered-By: Express"],
            "ASP.NET":     ["__VIEWSTATE","ASP.NET","aspnetcore"],
            "PHP":         ["X-Powered-By: PHP","PHPSESSID"],
            "Nginx":       ["Server: nginx"],
            "Apache":      ["Server: Apache"],
            "CloudFlare":  ["CF-RAY","cloudflare"],
            "AWS":         ["amazonaws","aws-cf-id","x-amz"],
            "Google Cloud":["x-goog","storage.googleapis"],
        }
        results={}
        for target in targets[:5]:
            _,headers=run(f"curl -sk --max-time 8 {pcurl} -I '{target}'",timeout=12)
            _,body=run(f"curl -sk --max-time 8 {pcurl} '{target}' | head -c 30000",timeout=12)
            combined=(headers+body).lower()
            detected=[]
            for tech,sigs in tech_sigs.items():
                if any(s.lower() in combined for s in sigs):
                    detected.append(tech)
            if detected:
                results[target]=detected
                with open(out,"a") as f:
                    f.write(f"{target}:\n  "+", ".join(detected)+"\n\n")
                for tech in detected:
                    self.db.add_finding(self.sid,type="Technology",severity="info",
                        url=target,title=f"Detected: {tech}",tool="mrx-tech")
        sp.stop(True)
        if results:
            for target,techs in results.items():
                li(f"  {p(A.GRY,target[:50])}")
                li(f"    → {p(A.CYN,', '.join(techs))}")

    # ── M19: API Security Test ────────────────────────
    def m19_api(self):
        lstep(19,"API Security Testing"); self._dash_step("API Testing")
        api_out=self._p("api_findings.txt"); pcurl=self._pcurl()
        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:10]
        else: targets=[f"https://{self.domain}"]
        sp=Spin("API endpoint discovery & testing","bounce",A.PURP); sp.start()
        api_paths=["/api","/api/v1","/api/v2","/v1","/v2","/graphql",
                   "/swagger.json","/openapi.json","/api-docs",
                   "/swagger/v1/swagger.json","/.well-known/openid-configuration",
                   "/api/swagger","/docs/api","/api/docs"]
        for target in targets[:5]:
            for path in api_paths:
                _,resp=run(f"curl -sk --max-time 6 {pcurl} "
                           f"'{target}{path}' -o /dev/null -w '%{{http_code}}'",timeout=9)
                if resp.strip() in ("200","401","403"):
                    _,body=run(f"curl -sk --max-time 6 {pcurl} '{target}{path}'",timeout=9)
                    content_type="json" if "{" in body[:200] else "other"
                    with open(api_out,"a") as f:
                        f.write(f"[{resp.strip()}] {target}{path} ({content_type})\n")
                    sev="medium" if resp.strip()=="200" else "low"
                    self.db.add_finding(self.sid,type="API Endpoint",severity=sev,
                        url=f"{target}{path}",title=f"API endpoint found [{resp.strip()}]",
                        tool="mrx-api")
                    self._dash_event(f"API [{resp.strip()}]: {path}",sev)
        sp.stop(True)
        n=clines(api_out)
        if n: lfound(f"API endpoints: {p(A.YEL+A.BOLD,str(n))}","medium")

    # ── M20: Rate Limit & Auth Test ───────────────────
    def m20_auth(self):
        lstep(20,"Authentication & Rate Limit Testing"); self._dash_step("Auth Testing")
        d=self.domain; out=self._p("auth_issues.txt"); pcurl=self._pcurl()
        targets=[]
        if self.live_file and self.live_file.exists():
            with open(self.live_file) as f: targets=[l.strip() for l in f][:5]
        else: targets=[f"https://{self.domain}"]
        sp=Spin("Testing login endpoints for rate limiting","scan",A.LRED); sp.start()
        login_paths=["/login","/signin","/auth","/api/login","/api/auth",
                     "/wp-login.php","/admin/login","/user/login"]
        issues_found=0
        for target in targets[:3]:
            for path in login_paths:
                url=f"{target}{path}"
                # Check if path exists
                _,code=run(f"curl -sk --max-time 5 {pcurl} -o /dev/null "
                           f"-w '%{{http_code}}' '{url}'",timeout=8)
                if code.strip() not in ("200","302","401"): continue
                # Rate limit test (3 rapid requests)
                codes=[]
                for _ in range(5):
                    _,rc=run(f"curl -sk --max-time 3 {pcurl} -o /dev/null "
                             f"-w '%{{http_code}}' -X POST '{url}' "
                             f"-d 'username=admin&password=wrongpassword'",timeout=5)
                    codes.append(rc.strip())
                # If all codes are same (no rate limiting / lockout)
                if len(set(codes))==1 and codes[0] in ("200","302","401"):
                    with open(out,"a") as f:
                        f.write(f"[NO RATE LIMIT] {url} — responses: {codes}\n")
                    self.db.add_finding(self.sid,type="No Rate Limiting",
                        severity="medium",url=url,
                        title="Login endpoint has no rate limiting",tool="mrx-auth")
                    issues_found+=1
                    self._dash_event(f"No rate limit: {path}","medium")
        sp.stop(True)
        if issues_found:
            lfound(f"Auth issues: {p(A.YEL+A.BOLD,str(issues_found))}","medium")
        else: li("No obvious rate limiting issues found (manual verification recommended)")

    # ── FINAL REPORT ───────────────────────────────────
    def print_summary(self, start_time:float):
        elapsed=time.time()-start_time
        mins,secs=int(elapsed//60),int(elapsed%60)
        stats=self.db.stats(self.sid)
        w=min(tw(),110)
        print()
        # Animated summary header
        title_line=grad("  ◈  MRX SCAN COMPLETE  ◈  ",GOLD)
        print(p(A.CYN+A.BOLD,"╔"+"═"*(w-2)+"╗"))
        print(p(A.CYN+A.BOLD,"║")+center(title_line,w-2)+p(A.CYN+A.BOLD,"║"))
        print(p(A.CYN+A.BOLD,"╚"+"═"*(w-2)+"╝"))
        print()

        meta=[
            ("🎯 Target",   p(A.CYN+A.BOLD,self.domain)),
            ("📁 Output",   p(A.GRY,str(self.outdir))),
            ("💾 Database", p(A.GRY,str(self.outdir/"results.db"))),
            ("⏱  Duration", p(A.YEL,f"{mins}m {secs}s")),
            ("📅 Date",     p(A.GRY,datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        ]
        for k,v in meta: print(f"  {p(A.GRY,k+':')}  {v}")

        print(f"\n  {p(A.GRY+A.DIM,'─'*w)}")
        items=[
            ("Subdomains", stats['subs'],  A.BLU,  "🌐"),
            ("Live Hosts", stats['alive'], A.GRN,  "✅"),
            ("Open Ports", stats['ports'], A.ORG,  "🔌"),
            ("URLs",       stats['urls'],  A.CYN,  "🔗"),
            ("Dirs",       stats['dirs'],  A.PURP, "📂"),
            ("Findings",   stats['finds'], A.YEL,  "🔍"),
            ("Critical",   stats['crit'],  A.RED,  "💀"),
            ("High",       stats['high'],  A.LRED, "🔥"),
        ]
        for i in range(0,len(items),4):
            row=items[i:i+4]
            print("  "+"".join(
                f"{ic} {p(cl+A.BOLD,str(val)):>12}  {p(A.GRY,lb):<16}  "
                for lb,val,cl,ic in row))

        print(f"\n  {p(A.GRY+A.DIM,'─'*w)}")
        lsec("GENERATED REPORTS","📄")
        reports=[
            ("report.html",   A.GRN,  "Interactive HTML report"),
            ("report.json",   A.CYN,  "Machine-readable JSON"),
            ("report.md",     A.YEL,  "Markdown summary"),
            ("findings.csv",  A.ORG,  "CSV spreadsheet"),
            ("findings.txt",  A.LWHT, "Plain text findings"),
            ("results.db",    A.PURP, "SQLite database"),
            ("bbhunt.log",    A.GRY,  "Full operation log"),
        ]
        for fname,color,desc in reports:
            fpath=self._p(fname)
            if fpath.exists():
                n=clines(fpath)
                print(f"  {p(color,fname):<30}  {p(A.GRY,desc)}")

        lsec("NEXT STEPS","💡")
        tips=[
            (A.LRED,"Open report.html in your browser for the full interactive report"),
            (A.RED, "Review nuclei_all.txt — verify each finding before submitting"),
            (A.ORG, "Load all_urls.txt into Burp Suite for manual testing"),
            (A.YEL, "Check dirs.txt for 403 responses — try bypass techniques"),
            (A.CYN, "Inspect js_secrets.txt — validate exposed keys/tokens"),
            (A.GRN, "SQLite: sqlite3 results.db 'SELECT * FROM findings WHERE severity=\"critical\"'"),
            (A.MAG, "For IDOR: test numeric IDs across all live.txt endpoints"),
        ]
        for color,tip in tips:
            print(f"    {p(color,'→')}  {p(A.LWHT,tip)}")
        print()
        print(center(grad("◈ ◈ ◈  MRX — Advanced Bug Bounty Framework  ◈ ◈ ◈",CYBER)))
        print(p(A.CYN+A.DIM,"═"*w)); print()

# ══════════════════════════════════════════════════════
#  INTERACTIVE MENU
# ══════════════════════════════════════════════════════
MODULES=[
    ("01","Subdomain Enumeration",       "subfinder,amass,assetfinder,dnsx,crt.sh",  True),
    ("02","Live Host Detection",          "httpx + tech fingerprint",                 True),
    ("03","Port Scanning",               "naabu,nmap",                               True),
    ("04","Directory Fuzzing",           "ffuf,feroxbuster",                         True),
    ("05","URL & Parameter Collection",  "gau,waybackurls,katana,gf",               True),
    ("06","JavaScript & Secrets",        "17-pattern scanner+LinkFinder",            False),
    ("07","Nuclei Auto-Scan",            "nuclei 9 template sets",                   True),
    ("08","XSS Scanning",               "dalfox",                                   True),
    ("09","SQL Injection",              "sqlmap",                                   False),
    ("10","Subdomain Takeover",         "subzy",                                    True),
    ("11","CORS Misconfiguration",      "curl-based",                               False),
    ("12","Nikto Web Server",           "nikto",                                    False),
    ("13","SSL/TLS Audit",             "python-ssl + testssl.sh",                  False),
    ("14","DNS Reconnaissance",        "dig + zone transfer",                       False),
    ("15","S3/Cloud Buckets",          "custom bucket enum",                        False),
    ("16","WordPress Scanner",         "wpscan + manual checks",                    False),
    ("17","Email Harvesting",          "crt.sh + URL grep",                         False),
    ("18","Technology Stack",          "17-signature detector",                     False),
    ("19","API Security",             "REST/GraphQL endpoint discovery",            False),
    ("20","Auth & Rate Limit",        "login endpoint tester",                      False),
]

def interactive_menu()->List[str]:
    selected={d[0]:d[3] for d in MODULES}

    def render():
        os.system("clear"); print_banner(animated=False)
        lsec("SELECT MODULES","⚙")
        print(f"  {p(A.GRY,'[number] toggle  |  A = all  |  N = none  |  Enter = start')}\n")
        for num,label,tools,_ in MODULES:
            is_sel=selected[num]
            icon=p(A.GRN+A.BOLD,"◉ ") if is_sel else p(A.DGRY,"○ ")
            lbl=p(A.WHT+A.BOLD,f"{num}. {label}") if is_sel else p(A.GRY,f"{num}. {label}")
            tl=p(A.DGRY,f"  [{tools}]")
            mark=p(A.DGRN," ✦") if is_sel else ""
            print(f"  {icon}{lbl}{mark}")
            print(f"     {tl}")
        count=sum(1 for v in selected.values() if v)
        print(f"\n  {p(A.CYN,str(count))} modules selected")

    render()
    while True:
        try: ans=input(f"\n  {p(A.CYN,'⟩')} ").strip().lower()
        except (EOFError,KeyboardInterrupt): sys.exit(0)
        if ans=="": break
        elif ans=="a":
            for k in selected: selected[k]=True
        elif ans=="n":
            for k in selected: selected[k]=False
        elif ans in selected:
            selected[ans]=not selected[ans]
        render()

    return [k for k,v in selected.items() if v]

# ══════════════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════════════
def main():
    parser=argparse.ArgumentParser(
        description="MRX — Advanced Bug Bounty Framework v4.0",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""Examples:
  python3 mrx.py -d example.com
  python3 mrx.py -d example.com --all --auto-install
  python3 mrx.py -d example.com --steps 1,2,7 --proxy-auto
  python3 mrx.py -d example.com --proxy-file proxies.txt
  python3 mrx.py --install-tools --auto-install
  python3 mrx.py -d example.com --all --aggressive --deep
  python3 mrx.py --db-query "SELECT * FROM findings WHERE severity='critical'"
""")
    parser.add_argument("-d","--domain",     help="Target domain")
    parser.add_argument("-o","--output",     help="Output directory")
    parser.add_argument("--steps",           help="Steps: 1,2,7")
    parser.add_argument("--all",action="store_true",help="Run all modules")
    parser.add_argument("--auto-install",action="store_true",help="Auto-install tools")
    parser.add_argument("--install-tools",action="store_true",help="Install tools & exit")
    parser.add_argument("--proxy-auto",action="store_true",help="Auto-fetch & use proxies")
    parser.add_argument("--proxy-file",     help="Load proxies from file")
    parser.add_argument("--proxy-setup",action="store_true",help="Interactive proxy setup")
    parser.add_argument("--aggressive",action="store_true",help="Aggressive scanning")
    parser.add_argument("--deep",action="store_true",help="Deep/recursive scanning")
    parser.add_argument("--no-banner",action="store_true",help="Skip banner")
    parser.add_argument("--no-dash",   action="store_true", help="No live dashboard")
    parser.add_argument("--proxy-test",action="store_true", help="Test proxies & exit")
    parser.add_argument("--show-modules",action="store_true",help="List all modules & exit")
    parser.add_argument("--version",   action="store_true", help="Show version & exit")
    parser.add_argument("--db-query",       help="SQL query on results DB")
    args=parser.parse_args()

    if not args.no_banner: print_banner(animated=True)
    else: print_banner(animated=False)

    # ── Version ──
    if args.version:
        print(f"  {p(A.CYN+A.BOLD,'MRX')} Bug Bounty Framework {p(A.YEL,'v4.0')}")
        print(f"  {p(A.GRY,'20 modules · Auto-proxy · SQLite DB · 6 report formats')}")
        sys.exit(0)

    # ── Show modules ──
    if args.show_modules:
        lsec("ALL MODULES","📋")
        for num,label,tools,req in MODULES:
            r = p(A.GRN,"[DEFAULT]") if req else p(A.GRY,"[optional]")
            print(f"  {p(A.CYN,num+'.')}  {p(A.WHT+A.BOLD,label):<35} {r}")
            print(f"       {p(A.DGRY,tools)}")
        sys.exit(0)

    # ── Install only ──
    if args.install_tools:
        check_tools(list(TOOLS.keys()),auto=args.auto_install)
        lok("Done"); sys.exit(0)

    # ── Get domain ──
    domain=args.domain
    if not domain:
        print(f"  {p(A.YEL,'Example:')} example.com\n")
        try: domain=input(f"  {p(A.CYN,'⟩')} Target domain: ").strip()
        except (EOFError,KeyboardInterrupt): sys.exit(0)
        if not domain: le("Domain required!"); sys.exit(1)
    domain=re.sub(r'^https?://','',domain).strip().strip("/")

    # ── Output dir ──
    ts=datetime.now().strftime("%Y%m%d_%H%M%S")
    outdir=Path(args.output) if args.output else Path(f"mrx_results/{domain}_{ts}")
    outdir.mkdir(parents=True,exist_ok=True)

    # ── Logging ──
    global _log_file; _log_file=str(outdir/"bbhunt.log")

    # ── Database ──
    db=DB(str(outdir/"results.db"))

    # ── DB query mode ──
    if args.db_query:
        try:
            rows=db.conn.execute(args.db_query).fetchall()
            c=db.conn.execute(args.db_query); cols=[d[0] for d in c.description or []]
            if cols: print("  "+p(A.CYN,"  ".join(cols)))
            for row in rows: print("  "+"  ".join(str(v) for v in row))
        except Exception as e: le(f"DB error: {e}")
        db.close(); sys.exit(0)

    # ── Config ──
    cfg={"aggressive":args.aggressive,"deep":args.deep,"auto":args.auto_install}
    sid=db.new_scan(domain,cfg)

    # ── Proxy Manager ──
    pm=ProxyManager(db,outdir)
    if args.proxy_auto:
        n=pm.fetch_public_proxies(600)
        if n>0:
            proxies=pm.proxy_file.read_text().splitlines()
            pm.test_proxies(proxies,max_workers=100,timeout=5)
    elif args.proxy_file:
        n=pm.load_from_file(args.proxy_file)
        if n>0: pm.test_proxies(pm.proxy_file.read_text().splitlines())
    elif args.proxy_setup:
        pm.interactive_menu()

    if pm.proxies:
        lok(f"Using {p(A.GRN+A.BOLD,str(len(pm.proxies)))} alive proxies (rotating)")

    # ── Tool check ──
    required=["subfinder","amass","httpx","nmap","naabu","ffuf","gau",
               "waybackurls","nuclei","dalfox","sqlmap","nikto","subzy",
               "gf","qsreplace","katana","anew","dnsx"]
    check_tools(required,auto=args.auto_install,db=db)

    # ── Step selection ──
    if args.steps:
        selected=[s.strip().zfill(2) for s in args.steps.split(",")]
    elif args.all:
        selected=[m[0] for m in MODULES]
    else:
        selected=interactive_menu()

    if not selected:
        le("No modules selected!"); db.close(); sys.exit(1)

    # ── Info ──
    os.system("clear"); print_banner(animated=False)
    li(f"Target:   {p(A.CYN+A.BOLD,domain)}")
    li(f"Output:   {p(A.GRY,str(outdir))}")
    li(f"Modules:  {p(A.YEL,str(len(selected)))} selected")
    li(f"Proxies:  {p(A.GRN,str(len(pm.proxies)))} alive")
    li(f"Mode:     {p(A.ORG,'AGGRESSIVE' if args.aggressive else 'STANDARD')}")
    print()

    # ── Signal handler ──
    def bye(sig,frame):
        print(f"\n\n  {p(A.YEL,'⚠')}  {p(A.YEL,'Interrupted by user')}")
        db.finish_scan(sid); db.close()
        print(A.SHOW_C,end=""); sys.exit(0)
    signal.signal(signal.SIGINT,bye); signal.signal(signal.SIGTERM,bye)

    # ── Workflow ──
    mrx=MRX(domain,outdir,db,sid,cfg,pm)
    if not args.no_dash: mrx.start_dash()
    start=time.time()

    step_map={
        "01":mrx.m01_subdomains, "02":mrx.m02_live,    "03":mrx.m03_ports,
        "04":mrx.m04_fuzz,       "05":mrx.m05_urls,    "06":mrx.m06_js,
        "07":mrx.m07_nuclei,     "08":mrx.m08_xss,     "09":mrx.m09_sqli,
        "10":mrx.m10_takeover,   "11":mrx.m11_cors,    "12":mrx.m12_nikto,
        "13":mrx.m13_ssl,        "14":mrx.m14_dns,     "15":mrx.m15_buckets,
        "16":mrx.m16_wordpress,  "17":mrx.m17_emails,  "18":mrx.m18_tech,
        "19":mrx.m19_api,        "20":mrx.m20_auth,
    }

    for step in selected:
        key=step.zfill(2); fn=step_map.get(key)
        if fn:
            try: fn()
            except KeyboardInterrupt: bye(None,None)
            except Exception as e: le(f"Module {key} error: {e}")

    # ── Reports ──
    mrx.stop_dash()
    out_mgr=OutputManager(outdir,db,sid,domain)
    out_mgr.generate_all(start)

    db.finish_scan(sid)
    mrx.print_summary(start)
    db.close()

if __name__=="__main__":
    main()
