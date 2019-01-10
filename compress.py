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

#if r:
#    print "name=%s, w=%d, h=%d\n" % (r['name'], r['w'], r['h'], )
#    print "bits:\n%s\n" % (r['bits'], )

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

def _store_count(f, pref, n):
    while True:
        if n >= 0x40:
            cnt = 0x40 - 1
        else:
            cnt = n
        f.write("0x%X, " % ( pref + cnt, ))
        n = n - cnt
        if n <= 0:
            break

def _if_store_0(f):
    global n0
    if n0 > 0:
#        print "n0 = %d\n" % (n0, )
        _store_count(f, 0x00, n0)
    n0 = 0

def _if_store_1(f):
    global n1
    if n1 > 0:
#        print "n1 = %d\n" % (n1, )
        _store_count(f, 0x40, n1)
    n1 = 0

def _if_store_x(f, bits, i):
    global nx
    if nx > 0:
#        print "nx = %d\n" % (nx, )
        _store_count(f, 0x80, nx)
        for j in bits[i - nx:i]:
            f.write("0x%X, " % ( j, ))
    nx = 0


for i in xrange(len(bits)):
    c = bits[i]
    if c == 0:
        n0 = n0 + 1
#       print "n0 = %d\n" % (n0, )
        _if_store_1(f)
        _if_store_x(f, bits, i)
    elif c == 0xff:
        n1 = n1 + 1
#       print "n1 = %d\n" % (n1, )
        _if_store_0(f)
        _if_store_x(f, bits, i)
    else:
        if nx == 0x40 - 1:
            _if_store_x(f, bits, i)
        nx = nx + 1
#       print "nx = %d\n" % (nx, )
        _if_store_0(f)
        _if_store_1(f)
_if_store_0(f)
_if_store_1(f)
_if_store_x(f, bits, i)

f.write("};\n")
f.close()

