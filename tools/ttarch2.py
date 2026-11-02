"""Lettore minimale di archivi Telltale .ttarch2 (NCTT/ZCTT, TTA3/TTA4)."""
import struct, sys, zlib, os


class Arch:
    def __init__(self, path):
        self.path = path
        self.f = open(path, 'rb')
        magic = self.f.read(4)
        self.magic = magic
        if magic == b'NCTT':
            total, = struct.unpack('<Q', self.f.read(8))
            self.base = 12
            self.chunks = None
            self._read = self._read_plain
        elif magic in (b'ZCTT', b'ECTT'):
            self.chunk_sz, n = struct.unpack('<II', self.f.read(8))
            self.offs = struct.unpack('<%dQ' % (n + 1), self.f.read(8 * (n + 1)))
            self.cache = {}
            self._read = self._read_z
        else:
            raise ValueError('magic sconosciuto %r' % magic)
        self.pos = 0
        hdr = self._read(0, 4)
        self.ver = hdr
        p = 4
        if hdr == b'3ATT':
            p += 4
        elif hdr != b'4ATT':
            raise ValueError('header interno %r' % hdr)
        name_sz, files = struct.unpack('<II', self._read(p, 8)); p += 8
        ent_sz = 28
        raw = self._read(p, ent_sz * files); p += ent_sz * files
        names = self._read(p, name_sz); p += name_sz
        self.data_start = p
        self.files = []
        for i in range(files):
            crc, off, size, unk, blk, noff = struct.unpack_from('<QQIIHH', raw, i * ent_sz)
            npos = blk * 0x10000 + noff
            name = names[npos:names.index(b'\0', npos)].decode('latin-1')
            self.files.append((name, off, size))

    def _read_plain(self, off, n):
        self.f.seek(self.base + off)
        return self.f.read(n)

    def _chunk(self, i):
        c = self.cache.get(i)
        if c is None:
            self.f.seek(self.offs[i])
            comp = self.f.read(self.offs[i + 1] - self.offs[i])
            if self.magic == b'ECTT':
                raise ValueError('archivio cifrato')
            c = zlib.decompress(comp, -15)
            if len(self.cache) > 64:
                self.cache.clear()
            self.cache[i] = c
        return c

    def _read_z(self, off, n):
        out = bytearray()
        while n > 0:
            ci, co = divmod(off, self.chunk_sz)
            c = self._chunk(ci)
            take = c[co:co + n]
            out += take
            off += len(take); n -= len(take)
        return bytes(out)

    def read(self, name_off_size):
        name, off, size = name_off_size
        return self._read(self.data_start + off, size)


# CRC64 ECMA-182 sul nome in minuscolo: e' la chiave delle voci TTA4
_POLY = 0x42F0E1EBA9EA3693
_T = []
for _i in range(256):
    _c = _i << 56
    for _ in range(8):
        _c = ((_c << 1) ^ _POLY if _c & (1 << 63) else _c << 1) & 0xFFFFFFFFFFFFFFFF
    _T.append(_c)


def crc64(name):
    c = 0
    for b in name.lower().encode('latin-1'):
        c = (_T[((c >> 56) ^ b) & 0xFF] ^ (c << 8)) & 0xFFFFFFFFFFFFFFFF
    return c


def write_archive(path, files, compressed=False):
    """Scrive un archivio TTA4: NCTT (come quelli delle lingue) o ZCTT (come i _data).

    files: lista di (nome, bytes). Nomi e dati in ordine alfabetico,
    voci ordinate per CRC64, tabella nomi a blocchi di 0x10000.
    ZCTT: contenuto riempito a zeri fino a un multiplo di 0x10000, poi ogni
    blocco compresso in deflate raw, come negli originali.
    """
    files = sorted(files, key=lambda x: x[0].lower())
    names = bytearray()
    name_pos = {}
    for n, _ in files:
        enc = n.encode('latin-1') + b'\0'
        left = 0x10000 - len(names) % 0x10000
        if len(enc) > left:
            names += b'\0' * left
        name_pos[n] = len(names)
        names += enc
    name_sz = (len(names) + 0xFFFF) // 0x10000 * 0x10000
    names += b'\0' * (name_sz - len(names))
    offs = {}
    o = 0
    for n, d in files:
        offs[n] = o
        o += len(d)
    table = bytearray()
    for n, d in sorted(files, key=lambda x: crc64(x[0])):
        p = name_pos[n]
        table += struct.pack('<QQIIHH', crc64(n), offs[n], len(d), 0, p >> 16, p & 0xFFFF)
    inner = b'4ATT' + struct.pack('<II', name_sz, len(files)) + bytes(table) + bytes(names)
    if not compressed:
        with open(path, 'wb') as g:
            g.write(b'NCTT' + struct.pack('<Q', len(inner) + o))
            g.write(inner)
            for _, d in files:
                g.write(d)
        return
    inner = bytearray(inner)
    for _, d in files:
        inner += d
    inner += b'\0' * (-len(inner) % 0x10000)
    chunks = []
    for i in range(0, len(inner), 0x10000):
        co = zlib.compressobj(9, zlib.DEFLATED, -15)
        chunks.append(co.compress(bytes(inner[i:i + 0x10000])) + co.flush())
    offs = [12 + 8 * (len(chunks) + 1)]
    for c in chunks:
        offs.append(offs[-1] + len(c))
    with open(path, 'wb') as g:
        g.write(b'ZCTT' + struct.pack('<II', 0x10000, len(chunks)))
        g.write(struct.pack('<%dQ' % len(offs), *offs))
        for c in chunks:
            g.write(c)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'list':
        for p in sys.argv[2:]:
            a = Arch(p)
            exts = {}
            for n, o, s in a.files:
                e = os.path.splitext(n)[1].lower()
                exts[e] = exts.get(e, 0) + 1
            print('%s %s %s files=%d %s' % (os.path.basename(p), a.magic.decode(), a.ver.decode(), len(a.files),
                                            ' '.join('%s:%d' % kv for kv in sorted(exts.items()))))
    elif cmd == 'names':
        a = Arch(sys.argv[2])
        pat = sys.argv[3].lower() if len(sys.argv) > 3 else ''
        for n, o, s in a.files:
            if pat in n.lower():
                print(n, s)
    elif cmd == 'extract':
        a = Arch(sys.argv[2]); out = sys.argv[3]
        pat = sys.argv[4].lower() if len(sys.argv) > 4 else ''
        os.makedirs(out, exist_ok=True)
        for e in a.files:
            if pat in e[0].lower():
                with open(os.path.join(out, e[0]), 'wb') as g:
                    g.write(a.read(e))
