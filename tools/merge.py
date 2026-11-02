"""Unisce la traduzione amatoriale 2014 con l'italiano ufficiale del Remastered.

Uso: python -I merge.py <Archives del gioco> <testi 2014> <cartella output> [traduzioni.txt]
                        [--originali <cartella con gli archivi originali salvati>]
                        [--nome bigby|luca]

<testi 2014>: il file dati/testi_2014.tsv oppure la cartella del pack 2014 originale.
--nome:       il nome del protagonista, Bigby (predefinito) o Luca.

Per ogni riga dei *_italian.landb del gioco, in ordine:
  -. correzioni forzate di traduzioni.txt (righe "! inglese ==> italiano"): vincono su tutto;
  0. crediti: blocco del team 2014 seguito dai crediti Telltale attuali;
  1. amatoriale per chiave, se l'inglese del 2014 coincide (o quasi) con quello attuale;
  2. amatoriale per testo, se la stessa frase inglese (3+ parole) e' tradotta altrove;
  3. amatoriale per testo su frasi brevi, solo se la traduzione 2014 e' sempre la stessa;
  4. traduzione manuale da traduzioni.txt (chiave = testo inglese normalizzato,
     "=" lascia il testo originale): ha la precedenza sull'ufficiale;
  5. ufficiale;
  6. altrimenti resta l'ufficiale (cioe' l'inglese) e la riga finisce in da_tradurre.tsv.
Su ogni riga tradotta, alla fine, NAMES (un solo nome per il protagonista) e i tag di
animazione {..} dell'inglese, se l'italiano non li ha uguali (lo slot e' l'inglese);
le voci delle righe delle Impostazioni (MENU_CP1252) si scrivono in cp1252, il resto in UTF-8.

Output: <out>/<archivio>/<nome>_italian.landb, report.txt, da_tradurre.tsv
"""
import difflib
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ttarch2 import Arch
from landb import Landb

NEW_ARCHIVES = ['Boot_ar_data', 'Fables101_ar_data', 'Fables102_ar_data', 'Fables103_ar_data',
                'Fables104_ar_data', 'Fables105_ar_data', 'Menu_ar_data', 'Project_ar_all']

# pack 2014, dal piu' vecchio al piu' recente: chi viene dopo vince
OLD_ARCHIVES = ['Fables_pc_Fables101_data', 'Fables_pc_Fables102_data', 'Fables_pc_Fables103_data',
                'Fables_pc_Fables104_data', 'Fables_pc_Fables105_data', 'Fables_pc_Menu_data',
                'Fables_pc_PC-Mac-TTG_Update_01_Fables101_all',
                'Fables_pc_PC-Mac_TTG_Update_02_Episode_02_Project_all']

# il protagonista: Bigby come nell'originale (predefinito) o Luca (da LUpo CAttivo) come
# nell'edizione italiana; le due traduzioni li mescolano, qui se ne usa uno solo
NAMES = {
    'bigby': [(r'\bLuca\b', 'Bigby'), (r'\bLUCA\b', 'BIGBY')],
    'luca': [(r'\bBigby\b', 'Luca'), (r'\bBIGBY\b', 'LUCA')],
}

# le righe delle Impostazioni (etichetta a sinistra, valore a destra) il gioco le legge come
# cp1252: scritte in UTF-8, "QUALITÀ" esce "QUALITÃÿ" e "SÌ" esce "SÃŒ". Titoli, elenchi e
# finestre di dialogo invece leggono UTF-8. Queste voci di ui_menu si scrivono quindi in cp1252
# (verificato nel gioco il 03/11/2026 con una build che mostrava il codice di ogni voce).
MENU_CP1252 = {
    0x1543311b,     # QUALITÀ GRAFICA
    0x1543313d,     # QUALITÀ TEXTURE
    0x15433135,     # QUALITÀ OMBRE
    0x1543331c,     # MODALITÀ NOIR
    0x1543310f,     # MODALITÀ MINIMALE
    0x15433108,     # LUMINOSITÀ
    0x15433125,     # SENSIBILITÀ MOUSE
    0x15433129,     # ON -> SÌ, valore
    0x15433183,     # ON -> SÌ, valore
}

# marcatore dei crediti del team della traduzione 2014
TEAM_MARK = 'CRYBIOLAB'

TOKEN = re.compile(r'\{[^}]*\}|\[[^\]]*\]')


def norm(s):
    s = TOKEN.sub(' ', s)
    s = s.replace('’', "'").replace('‘', "'").replace('“', '"').replace('”', '"')
    s = s.replace('…', '...').replace('. . .', '...').replace('—', '--').replace('–', '-')
    return re.sub(r'\s+', ' ', s).strip()


def clean(s):
    """Testo cosi' com'e': tag {..} e [..] restano, l'inglese li contiene e il gioco li gestisce.

    Le righe fatte solo di [..] sono le scelte d'azione mostrate al giocatore.
    """
    return s.strip()


def fix_mojibake(s):
    """Righe 2014 salvate due volte (UTF-8 letto come cp1252): "PiÃ¹" -> "Più"."""
    def fix(m):
        try:
            return m.group().encode('cp1252').decode('utf-8')
        except (UnicodeEncodeError, UnicodeDecodeError):
            return m.group()
    # coppia per coppia: nella stessa riga possono esserci anche lettere accentate giuste
    return re.sub(r'[ÃÂ].', fix, s)


TAG = re.compile(r'\{[^}]*\}')


def restore_tags(en, it):
    """Rimette i tag di animazione {..} dell'inglese se l'italiano non li ha uguali.

    Ogni tag torna all'inizio della frase in cui sta nell'inglese, se le due righe hanno
    lo stesso numero di frasi; altrimenti tutti all'inizio della riga.
    """
    tags = list(TAG.finditer(en))
    if not tags or TAG.findall(it) == [t.group() for t in tags]:
        return it
    end = r'(?<=[.!?])\s+'
    body = re.sub(r' {2,}', ' ', TAG.sub('', it)).strip()
    it_sents = re.split(end, body)
    en_sents = re.split(end, TAG.sub('', en).strip())
    same = len(it_sents) == len(en_sents)
    lead = [''] * len(it_sents)
    for t in tags:
        before = TAG.sub('', en[:t.start()]).strip()
        idx = len(re.split(end, before + ' x')) - 1 if same and before else 0
        lead[min(idx, len(it_sents) - 1)] += t.group()
    return ' '.join(l + s for l, s in zip(lead, it_sents))


def key(s):
    """Chiave di confronto: testo senza tag; per le righe fatte solo di tag, il tag stesso."""
    return norm(s) or re.sub(r'\s+', ' ', s).strip()


def words(s):
    return len(key(s).split())


def load_pack(pack):
    """chiave -> (inglese 2014, italiano amatoriale) dalla cartella del pack 2014, testo com'e'."""
    ref = {}    # chiave -> inglese 2014 (dai *_italian.landb non toccati dai traduttori)
    fan = {}    # chiave -> italiano amatoriale (dai *_english.landb)
    for an in OLD_ARCHIVES:
        a = Arch(os.path.join(pack, an + '.ttarch2'))
        for e in a.files:
            n = e[0].lower()
            if n.endswith('_italian.landb'):
                L = Landb(n, a.read(e))
                ref.update({x.key: L.dec(x.text) for x in L.entries})
            elif n.endswith('_english.landb'):
                L = Landb(n, a.read(e))
                fan.update({x.key: L.dec(x.text) for x in L.entries})
    for f in sorted(os.listdir(pack)):
        if f.lower().endswith('_english.landb'):
            L = Landb(f, open(os.path.join(pack, f), 'rb').read())
            fan.update({x.key: L.dec(x.text) for x in L.entries})
    return {k: (ref[k], fan[k]) for k in fan if k in ref}


# testi_2014.tsv: a capo, tabulazioni e barre rovesciate scritti come \n \t \r \\
ESCAPES = {'\\': '\\\\', '\t': '\\t', '\n': '\\n', '\r': '\\r'}
UNESCAPES = {v[1]: k for k, v in ESCAPES.items()}


def tsv_escape(s):
    return ''.join(ESCAPES.get(c, c) for c in s)


def tsv_unescape(s):
    return re.sub(r'\\(.)', lambda m: UNESCAPES[m.group(1)], s)


def load_testi(path):
    """Lo stesso di load_pack, letto da testi_2014.tsv (creato da esporta_2014.py).

    Righe: chiave esadecimale, inglese 2014, italiano 2014. Le righe con # e l'intestazione
    si saltano. L'ordine delle righe conta: a parita' di frequenza vince la traduzione
    che compare prima, come con il pack.
    """
    out = {}
    with open(path, encoding='utf-8-sig') as f:
        for ln in f:
            ln = ln.rstrip('\n')
            if not ln or ln.startswith('#') or ln.startswith('chiave\t'):
                continue
            k, en, it = ln.split('\t')
            out[int(k, 16)] = (tsv_unescape(en), tsv_unescape(it))
    return out


def load_old(pack):
    """chiave -> (inglese 2014, italiano amatoriale).

    pack: il file testi_2014.tsv oppure la cartella del pack 2014 originale.
    """
    raw = load_testi(pack) if os.path.isfile(pack) else load_pack(pack)
    return {k: (en, fix_mojibake(it)) for k, (en, it) in raw.items()}


def load_tsv(path):
    """File delle traduzioni manuali: una riga per frase, "inglese ==> italiano".

    L'inglese e' quello normalizzato (come in da_tradurre.tsv), \\n nell'italiano va a capo.
    Le righe che iniziano con "! " sono correzioni forzate: valgono sopra ogni altra
    origine, anche sopra la traduzione 2014.
    """
    out, forced = {}, {}
    if path and os.path.exists(path):
        # utf-8-sig: il Blocco note puo' salvare con il BOM in testa
        for n, ln in enumerate(open(path, encoding='utf-8-sig'), 1):
            ln = ln.rstrip('\n')
            if not ln.strip() or ln.startswith('#'):
                continue
            target = out
            if ln.startswith('! '):
                target, ln = forced, ln[2:]
            if ' ==> ' not in ln:
                raise ValueError('%s, riga %d: manca " ==> " (spazio, uguale, due maggiore, spazio) '
                                 'tra inglese e italiano' % (os.path.basename(path), n))
            en, it = ln.split(' ==> ', 1)
            target[key(en)] = it.replace('\\n', '\n')
    return out, forced


def apply_names(s, nome='bigby'):
    """Il nome scelto, su tutta la riga (anche nelle indicazioni [..], che non si vedono:
    la traduzione 2014 aveva messo "Luca" anche li')."""
    for pat, rep in NAMES[nome]:
        s = re.sub(pat, rep, s)
    return s


def team_credits(old_en, fan_it, current):
    """Paragrafi del team 2014 (quelli che non vengono dall'inglese) + crediti attuali."""
    paras = fan_it.split('\n\n')
    team = []
    for p in paras:
        if p.strip() and p in old_en:
            break
        team.append(p)
    return '\n\n'.join(team).strip() + '\n\n' + current


def main():
    args = sys.argv[1:]
    originals = None
    if '--originali' in args:
        i = args.index('--originali')
        originals = args[i + 1]
        del args[i:i + 2]
    nome = 'bigby'
    if '--nome' in args:
        i = args.index('--nome')
        nome = args[i + 1].lower()
        del args[i:i + 2]
        if nome not in NAMES:
            raise SystemExit('--nome: bigby oppure luca')
    game, pack, out = args[0], args[1], args[2]
    manual, forced = load_tsv(args[3] if len(args) > 3 else None)
    old = load_old(pack)

    # frase inglese 2014 -> traduzioni amatoriali usate
    by_text = defaultdict(Counter)
    for en, it in old.values():
        if key(it) != key(en) and clean(it):
            by_text[key(en)][clean(it)] += 1

    stats = Counter()
    todo = {}
    used_manual = set()
    detail = []
    os.makedirs(out, exist_ok=True)
    for an in NEW_ARCHIVES:
        # con la traduzione installata alcuni *_english.landb sono gia' in italiano:
        # si parte dagli originali salvati, se ci sono
        fn = 'Fables_pc_%s.ttarch2' % an
        src = os.path.join(originals, fn) if originals else None
        a = Arch(src if src and os.path.exists(src) else os.path.join(game, fn))
        files = {e[0]: e for e in a.files}
        for name in sorted(files):
            if not name.endswith('_italian.landb'):
                continue
            E = Landb(name, a.read(files[name.replace('_italian', '_english')]))
            I = Landb(name, a.read(files[name]))
            en_by_key = {x.key: E.dec(x.text) for x in E.entries}
            for x in I.entries:
                en = en_by_key.get(x.key, '')
                off = I.dec(x.text)
                ne = key(en)
                if not ne:
                    stats['vuote'] += 1
                    continue
                src, text = None, None
                o = old.get(x.key)
                if ne in forced:
                    used_manual.add(ne)
                    src, text = 'correzione', forced[ne]
                elif o and TEAM_MARK in o[1]:
                    src, text = 'crediti_team', team_credits(o[0], o[1], clean(off))
                elif o:
                    oe, fi = o
                    same = key(oe) == ne
                    if same or difflib.SequenceMatcher(None, key(oe), ne).ratio() >= 0.9:
                        if clean(fi) and (key(fi) != key(oe) or words(oe) < 3):
                            src, text = ('amatoriale' if same else 'amatoriale_simile'), clean(fi)
                if text is None and ne in by_text:
                    variants = by_text[ne]
                    if words(en) >= 3:
                        src, text = 'amatoriale_testo', variants.most_common(1)[0][0]
                    elif len(variants) == 1:
                        src, text = 'amatoriale_breve', next(iter(variants))
                if text is None and ne in manual:
                    used_manual.add(ne)
                    if manual[ne] == '=':
                        src, text = 'mantenuta', clean(en)
                    else:
                        src, text = 'manuale', manual[ne]
                if text is None and key(off) != ne:
                    src, text = 'ufficiale', clean(off)
                if text is None:
                    src, text = 'inglese', clean(off)
                    todo.setdefault(ne, (an, name, I.dec(x.prefix), en))
                stats[src] += 1
                # righe rimaste in inglese e crediti (elenco con i nomi originali,
                # "BIGBY WOLF") restano com'erano
                if src not in ('inglese', 'mantenuta', 'crediti_team'):
                    text = apply_names(text, nome)
                text = restore_tags(en, text)
                detail.append((an, name, '%08x' % x.key, src, en, text))
                if name == 'ui_menu_italian.landb' and x.key in MENU_CP1252:
                    x.text = text.encode('cp1252', 'replace')
                else:
                    x.text = text.encode('utf-8')
            os.makedirs(os.path.join(out, an), exist_ok=True)
            I.write(os.path.join(out, an, name))

    esc = lambda s: s.replace('\\', '\\\\').replace('\t', '\\t').replace('\n', '\\n')
    with open(os.path.join(out, 'dettaglio.tsv'), 'w', encoding='utf-8') as g:
        g.write('archivio\tfile\tchiave\torigine\tinglese\titaliano\n')
        for row in detail:
            g.write('\t'.join(row[:4] + (esc(row[4]), esc(row[5]))) + '\n')
    with open(os.path.join(out, 'da_tradurre.tsv'), 'w', encoding='utf-8') as g:
        for ne, (an, name, who, en) in sorted(todo.items(), key=lambda kv: (kv[1][1], kv[0])):
            g.write('%s\t%s\t%s\t%s\n' % (ne, an, name, who))
    tot = sum(stats.values())
    rep = ['nome del protagonista: %s' % nome.capitalize(), 'righe totali: %d' % tot] + ['  %-18s %6d  %5.1f%%' % (k, v, 100.0 * v / tot)
                                        for k, v in stats.most_common()]
    rep.append('frasi inglesi uniche ancora da tradurre: %d' % len(todo))
    unused = sorted((set(manual) | set(forced)) - used_manual)
    rep.append('traduzioni manuali mai usate: %d' % len(unused))
    rep += ['  ' + u[:100] for u in unused]
    open(os.path.join(out, 'report.txt'), 'w', encoding='utf-8').write('\n'.join(rep) + '\n')
    print('\n'.join(rep))


if __name__ == '__main__':
    main()
