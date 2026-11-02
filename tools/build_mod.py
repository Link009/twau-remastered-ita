"""Crea la mod "italiano nello slot di un'altra lingua" per The Wolf Among Us Remastered.

Uso: python -I build_mod.py <cartella Archives> <cartella output> [cartella landb italiani]
                            [--originali <cartella>] [--slot english|spanish]

Senza il terzo argomento usa l'italiano ufficiale nascosto nel gioco (*_italian.landb).
Con il terzo argomento (l'output di merge.py: <cartella>/<archivio>/<nome>_italian.landb)
quei file prendono il posto di quelli ufficiali (traduzione ibrida).
--originali: cartella con le copie originali degli archivi gia' modificati (il backup),
             da cui ripartire invece che dagli archivi installati.
--slot:      lingua da sostituire (predefinita english: la nota legale cifrata nello
             script d'avvio resta in inglese invece che nella lingua dello slot).

I file dello slot si costruiscono dagli originali di quella lingua cambiando solo il testo:
struttura, flag e nomi dei personaggi restano quelli del gioco.

Produce:
  Fables_pc_italiano_ar_all.ttarch2  testi comuni a tutto il gioco
  _resdesc_50_italiano.lua           set "constant" con priorita' 900, sopra i set di lingua (800)
  archivi/Fables_pc_*.ttarch2
      copie di archivi del gioco con alcuni testi dello slot gia' in italiano, dove il set
      "constant" non basta: ui_episode e ui_credits (diversi in ogni episodio) e boot
      (schermata del logo, caricata prima che il set sia attivo)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ttarch2 import Arch, write_archive
from landb import Landb

# archivi del gioco che contengono i *_italian.landb
TEXT_ARCHIVES = ['Boot_ar_data', 'Fables101_ar_data', 'Fables102_ar_data', 'Fables103_ar_data',
                 'Fables104_ar_data', 'Fables105_ar_data', 'Menu_ar_data', 'Project_ar_all']

LANGS = ['english', 'french', 'german', 'spanish']

# voce della lingua dello slot nel menu (la prima di ogni gruppo e' quella di DISPLAY LANGUAGE)
LABELS = {
    'english': {0x15433332: 'Italiano', 0x15433051: 'Italiano', 0x1543311f: 'ITALIANO'},
    'spanish': {0x15433336: 'Italiano', 0x15433055: 'Italiano', 0x15433123: 'ITALIANO'},
}

# testi della schermata del logo: il gioco li legge prima di attivare il set "constant"
BOOT_TEXTS = ['boot_italian.landb']

# il set spagnolo sostituisce questi file con versioni tradotte: nello slot spagnolo
# rimettiamo quelle inglesi (lo slot inglese usa gia' quelle di base)
ENGLISH_ASSETS = {
    'spanish': {
        'obj_lettersBusinessOffice.d3dtx': 'ReFables103_ar_txmesh',
        'obj_letterToad.d3dtx': 'ReFables103_ar_txmesh',
        'ui_menu_list_button_new.d3dtx': 'Menu_ar_txmesh',
        'ui_menu_feed.scene': 'Menu_ar_data',
        'ui_menu_list_stat.scene': 'Menu_ar_data',
        'ui_menu_list_stat_lineup.scene': 'Menu_ar_data',
    },
}

# modello del file di registrazione: quello di un set di lingua esistente
RESDESC_TEMPLATE = 'spanish'


def arch(game, name, originals=None):
    fn = 'Fables_pc_%s.ttarch2' % name
    if originals and os.path.exists(os.path.join(originals, fn)):
        return Arch(os.path.join(originals, fn))
    return Arch(os.path.join(game, fn))


def italian_text(game_arch, entry, an, custom):
    """Il *_italian.landb dell'archivio: quello unito da merge.py se c'e', altrimenti l'ufficiale."""
    src = os.path.join(custom, an, entry[0]) if custom else None
    if src and os.path.exists(src):
        return open(src, 'rb').read(), True
    return game_arch.read(entry), False


def slot_name(name, slot):
    return name[:-len('_italian.landb')] + '_%s.landb' % slot


def slot_landb(game_arch, names, it_name, it_data, slot):
    """Il file originale della lingua dello slot con i testi italiani, riga per riga."""
    slot_entry = names[slot_name(it_name, slot).lower()]
    S = Landb(slot_entry[0], game_arch.read(slot_entry))
    texts = {e.key: e.text for e in Landb(it_name, it_data).entries}
    if [e.key for e in S.entries] != list(texts):
        raise ValueError('%s: righe diverse tra italiano e %s' % (it_name, slot))
    for e in S.entries:
        e.text = texts[e.key]
    return slot_entry[0], S.to_bytes()


def relabel(name, data, slot):
    L = Landb(name, data)
    for key, text in LABELS[slot].items():
        if not L.set_text(key, text):
            raise ValueError('%s: voce 0x%x non trovata' % (name, key))
    return L.to_bytes()


def main():
    args = sys.argv[1:]
    originals = slot = None
    if '--originali' in args:
        i = args.index('--originali')
        originals = args[i + 1]
        del args[i:i + 2]
    slot = 'english'
    if '--slot' in args:
        i = args.index('--slot')
        slot = args[i + 1]
        del args[i:i + 2]
    game, out = args[0], args[1]
    custom = args[2] if len(args) > 2 else None
    os.makedirs(out, exist_ok=True)
    files = {}

    # ui_credits e ui_episode esistono in ogni episodio con contenuto diverso: un set
    # "constant" ne imporrebbe una sola versione a tutti, quindi restano fuori
    archives = {an: arch(game, an, originals) for an in TEXT_ARCHIVES}
    seen = {}
    for an, a in archives.items():
        for e in a.files:
            seen[e[0].lower()] = seen.get(e[0].lower(), 0) + 1
    per_episode = sorted(n for n, c in seen.items() if c > 1 and n.endswith('_italian.landb'))

    used_custom = 0
    other_menus = ['ui_menu_%s.landb' % l for l in LANGS if l != slot]
    for an, a in archives.items():
        names = {e[0].lower(): e for e in a.files}
        for e in a.files:
            name = e[0]
            if name.lower() in per_episode:
                continue
            if name.lower().endswith('_italian.landb'):
                data, is_custom = italian_text(a, e, an, custom)
                used_custom += is_custom
                out_name, out_data = slot_landb(a, names, name, data, slot)
                files[out_name] = out_data
            elif an == 'Menu_ar_data' and name.lower() in other_menus:
                files[name] = relabel(name, a.read(e), slot)

    slot_menu = 'ui_menu_%s.landb' % slot
    files[slot_menu] = relabel(slot_menu, files[slot_menu], slot)

    for name, an in ENGLISH_ASSETS.get(slot, {}).items():
        a = arch(game, an)
        e = next(x for x in a.files if x[0].lower() == name.lower())
        files[e[0]] = a.read(e)

    arch_name = 'Fables_pc_italiano_ar_all.ttarch2'
    write_archive(os.path.join(out, arch_name), list(files.items()))

    src = open(os.path.join(game, '_resdesc_50_%s.lua' % RESDESC_TEMPLATE), 'rb').read()
    for old, new in [(b'set.priority = 800', b'set.priority = 900'),
                     (b'set.enableMode = "localization"', b'set.enableMode = "constant"'),
                     (RESDESC_TEMPLATE.encode(), b'italiano')]:
        if old not in src:
            raise ValueError('resdesc: %r non trovato' % old)
        src = src.replace(old, new)
    open(os.path.join(out, '_resdesc_50_italiano.lua'), 'wb').write(src)

    # verifica: l'archivio si rilegge e ogni landb si analizza
    check = Arch(os.path.join(out, arch_name))
    n_landb = 0
    for e in check.files:
        if e[0].endswith('.landb'):
            Landb(e[0], check.read(e))
            n_landb += 1
    check.f.close()
    print('slot: %s' % slot)
    print('%s: %d file (%d landb, %d dalla cartella personalizzata), %.1f MB'
          % (arch_name, len(check.files), n_landb, used_custom,
             os.path.getsize(os.path.join(out, arch_name)) / 1e6))

    # archivi del gioco: stesso contenuto, sostituiti solo i file dello slot che il set non copre
    ep_dir = os.path.join(out, 'archivi')
    os.makedirs(ep_dir, exist_ok=True)
    for an, a in archives.items():
        names = {e[0].lower(): e for e in a.files}
        todo = [n for n in per_episode + BOOT_TEXTS if n in names]
        if not todo:
            continue
        repl = {}
        for n in todo:
            data, is_custom = italian_text(a, names[n], an, custom)
            out_name, out_data = slot_landb(a, names, names[n][0], data, slot)
            repl[out_name.lower()] = out_data
        content = [(e[0], repl.get(e[0].lower()) or a.read(e)) for e in a.files]
        dst = os.path.join(ep_dir, 'Fables_pc_%s.ttarch2' % an)
        write_archive(dst, content, compressed=a.magic == b'ZCTT')
        check = Arch(dst)
        ok = len(check.files) == len(a.files) and all(
            check.read(e) == (repl.get(e[0].lower()) or a.read(names[e[0].lower()])) for e in check.files)
        check.f.close()
        print('%s: %d file, sostituiti %s, rilettura %s'
              % (os.path.basename(dst), len(check.files), ', '.join(sorted(repl)), 'ok' if ok else 'ERRORE'))
        if not ok:
            raise ValueError('rilettura di %s non coincide' % dst)


if __name__ == '__main__':
    main()
