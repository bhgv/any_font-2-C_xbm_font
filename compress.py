#!/usr/bin/python

import sys
import re


# XBM header
xbm_head = re.compile(
    br"\s*#define[ \t]+(?P<name>.*)_width[ \t]+(?P<width>[0-9]+)[\r\n]+"
    b"#define[ \t]+.*_height[ \t]+(?P<height>[0-9]+)[\r\n]+"
    b"(?P<hotspot>"
    b"#define[ \t]+[^_]*_x_hot[ \t]+(?P<xhot>[0-9]+)[\r\n]+"
    b"#define[ \t]+[^_]*_y_hot[ \t]+(?P<yhot>[0-9]+)[\r\n]+"
    b")?"
    b"[\\000-\\377]*_bits\\[\\]"
    b"\s*=\s*\{[\r\n]+"
    b"(?P<bits>([\s\r\n]*0x[0-9a-fA-F]+,)+)"
)

xbm_bytes = re.compile(br"0x[0-9a-fA-F]+")

fpn = sys.argv[1]

tmp = fpn.split('/')

fn = tmp[-1]
fp = '/'.join(tmp[:-1])
if fp == '':
    fp = '.'

#print "fn = %s\nfp = %s\n" % (fn, fp, )

def xbm_rd(txt):
    m = xbm_head.match(txt)
    if m:
        w = int(m.group("width"))
        h = int(m.group("height"))

        if m.group("hotspot"):
            xhot = int(m.group("xhot"))
            yhot = int(m.group("yhot"))

        bits = xbm_bytes.findall(m.group("bits"))
        return {
            'name': m.group("name"),
            'w': w,
            'h': h,
            'bits': [int(a, 16) for a in bits],
        }


f = open(fpn, "r")
txt = f.read()
f.close()

r = xbm_rd(txt)

w = r['w']
h = r['h']
nm = r['name']
bits = r['bits']

f = open(fp + "/z"+fn, "w")
f.write("#define\tz" + nm + "_width\t"  + str(w) + "\n")
f.write("#define\tz" + nm + "_height\t" + str(h) + "\n")
f.write("static char z" + nm + "_bits[] = {\n")

n0 = 0
n1 = 0
nx = 0

a_ttl  = []
a_posx = []


def encode_x_dobles():
    global a_ttl, a_posx

    i = 0
    i_max = len(a_posx)
    while i < i_max:
        j = a_posx[i]
        ln = a_ttl[j]

        i_from = i-64
        if i_from < 0:
            i_from = 0

        for k in xrange(i_from, i):
            k_a_ttl = a_posx[k]

            if ln == a_ttl[k_a_ttl]:
                a_ttl[j] = [0xC0 + (k-i_from)]
                del a_posx[i]
                i = i - 1
                i_max = i_max - 1
                break
        i = i + 1



def _store_count(f, pref, n):
    global a_ttl, a_posx
    pos_ttl = -1
    while True:
        if n >= 0x40:
            cnt = 0x40 - 1
        else:
            cnt = n

#        f.write("0x%X, " % ( pref + cnt, ))
        a_ttl.append([pref + cnt,])
        pos_ttl = len(a_ttl) - 1
        if pref == 0x80:
            a_posx.append(pos_ttl)

        n = n - cnt
        if n <= 0:
            break
    return pos_ttl

def _if_store_0(f):
    global n0
    if n0 > 0:
        _store_count(f, 0x00, n0)
    n0 = 0

def _if_store_1(f):
    global n1
    if n1 > 0:
        _store_count(f, 0x40, n1)
    n1 = 0

def _if_store_x(f, bits, i):
    global nx
    if nx > 0:
        pos = _store_count(f, 0x80, nx)
        for j in bits[i - nx:i]:
            a_ttl[pos].append(j)
#            f.write("0x%X, " % ( j, ))
    nx = 0


for i in xrange(len(bits)):
    c = bits[i]
    if c == 0:
        n0 = n0 + 1
        _if_store_1(f)
        _if_store_x(f, bits, i)
    elif c == 0xff:
        n1 = n1 + 1
        _if_store_0(f)
        _if_store_x(f, bits, i)
    else:
        if nx == 0x40 - 1:
            _if_store_x(f, bits, i)
        nx = nx + 1
        _if_store_0(f)
        _if_store_1(f)

_if_store_0(f)
_if_store_1(f)
_if_store_x(f, bits, i)

encode_x_dobles()

for ln in a_ttl:
#    f.write("    "),
    for i in ln:
        f.write("0x%X, " % ( i, ))
#    f.write("\n"),

#f.write("    ")
f.write("0x0,\n")

f.write("};\n")
f.close()

