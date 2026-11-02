"""Parser dei .landb Telltale (MSV5 = TWAU 2014, MSV6 = Remastered)."""
import struct


class Entry:
    __slots__ = ('key', 'pre', 'prefix', 'text', 'post', 'flags')


class Landb:
    def __init__(self, path, data=None):
        d = open(path, 'rb').read() if data is None else data
        self.path = path
        self.raw = d
        magic = d[:4]
        if magic not in (b'5VSM', b'6VSM'):
            raise ValueError('magic %r' % magic)
        self.ver = 5 if magic == b'5VSM' else 6
        self.def_sz, self.async_sz, _ = struct.unpack_from('<III', d, 4)
        ncls, = struct.unpack_from('<I', d, 16)
        p = 20 + ncls * 12
        self.hdr_end = p
        # 08 00 00 00 | u32 | 08 00 00 00 | u32 | u32 map_block_size | u32 count
        self.map_off = p + 16
        blk, cnt = struct.unpack_from('<II', d, self.map_off)
        self.map_end = self.map_off + blk
        p = self.map_off + 8
        self.entries = []
        for _ in range(cnt):
            e = Entry()
            start = p
            e.key, = struct.unpack_from('<I', d, p)
            # key(4) sym(8) id(4) 0(4) blk12 blk12 blk8 0(4)
            p += 4 + 8 + 4 + 4 + 12 + 12 + 8 + 4
            e.pre = d[start:p]
            lblk, = struct.unpack_from('<I', d, p)
            lend = p + lblk
            q = p + 4
            psz, plen = struct.unpack_from('<II', d, q)
            e.prefix = d[q + 8:q + 8 + plen]
            q += psz
            tsz, tlen = struct.unpack_from('<II', d, q)
            e.text = d[q + 8:q + 8 + tlen]
            q += tsz
            e.flags = d[q:lend]
            p = lend
            tail = 12 if self.ver == 6 else 4
            e.post = d[p:p + tail]
            p += tail
            self.entries.append(e)
        if p != self.map_end:
            raise ValueError('%s: parse finito a %d, atteso %d' % (path, p, self.map_end))
        self.rest = d[p:]

    def write(self, path):
        open(path, 'wb').write(self.to_bytes())

    def set_text(self, key, text):
        for e in self.entries:
            if e.key == key:
                e.text = text.encode('utf-8') if self.ver == 6 else text.encode('cp1252')
                return True
        return False

    def to_bytes(self):
        body = bytearray()
        for e in self.entries:
            body += e.pre
            pb = struct.pack('<II', 8 + len(e.prefix), len(e.prefix)) + e.prefix
            tb = struct.pack('<II', 8 + len(e.text), len(e.text)) + e.text
            inner = pb + tb + e.flags
            body += struct.pack('<I', 4 + len(inner)) + inner
            body += e.post
        d = self.raw
        mp = struct.pack('<II', 8 + len(body), len(self.entries)) + body
        delta = len(mp) - (self.map_end - self.map_off)
        out = bytearray(d[:self.map_off]) + mp + self.rest
        struct.pack_into('<I', out, 4, self.def_sz + delta)
        return bytes(out)

    def dec(self, b):
        try:
            return b.decode('utf-8') if self.ver == 6 else b.decode('cp1252')
        except UnicodeDecodeError:
            return b.decode('cp1252', 'replace')


if __name__ == '__main__':
    import sys
    L = Landb(sys.argv[1])
    for e in L.entries[:int(sys.argv[2]) if len(sys.argv) > 2 else 10]:
        print(hex(e.key), L.dec(e.prefix), '|', L.dec(e.text))
