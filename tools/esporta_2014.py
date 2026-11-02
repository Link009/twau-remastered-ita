"""Esporta i testi della traduzione 2014 del CRYBIOLAB TEAM in dati/testi_2014.tsv.

Uso: python -I esporta_2014.py <cartella del pack 2014> <file .tsv di uscita>

Il pack 2014 contiene archivi interi del gioco di allora; merge.py ne usa solo i testi:
per ogni riga la chiave, l'inglese del 2014 e la traduzione italiana. Questo script li
scrive in un file di testo, nello stesso ordine in cui merge.py li legge dal pack, cosi'
merge.py da' lo stesso risultato partendo dal file o dal pack.
Il testo resta com'e' nel pack (anche le 2 righe con la codifica rovinata, che merge.py
corregge in lettura).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from merge import load_pack, load_testi, tsv_escape

HEADER = [
    '# The Wolf Among Us: traduzione italiana del 2014 del CRYBIOLAB TEAM.',
    '# Colonne: chiave della riga (esadecimale), inglese del 2014, italiano. A capo scritti come \\n.',
    'chiave\tinglese_2014\titaliano_2014',
]


def main():
    pack, out = sys.argv[1], sys.argv[2]
    rows = load_pack(pack)
    with open(out, 'w', encoding='utf-8', newline='\n') as g:
        g.write('\n'.join(HEADER) + '\n')
        for k, (en, it) in rows.items():
            g.write('%08x\t%s\t%s\n' % (k, tsv_escape(en), tsv_escape(it)))
    # verifica: il file riletto deve dare le stesse righe nello stesso ordine
    back = load_testi(out)
    if list(back.items()) != list(rows.items()):
        raise ValueError('%s: il file riletto non coincide con il pack' % out)
    print('%s: %d righe, %.1f MB, rilettura ok' % (out, len(rows), os.path.getsize(out) / 1e6))


if __name__ == '__main__':
    main()
