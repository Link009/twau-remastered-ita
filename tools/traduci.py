"""Crea e installa la traduzione italiana di The Wolf Among Us Remastered con un solo comando.

Uso, a gioco chiuso (oppure trascinando la cartella del gioco su TRADUCI.bat o RIMUOVI.bat):
  python -I tools/traduci.py "<cartella del gioco>"              crea la traduzione e la installa
  python -I tools/traduci.py "<cartella del gioco>" --rimuovi    toglie la traduzione
  python -I tools/traduci.py "<cartella del gioco>" --solo-crea  crea i file senza installarli
  python -I tools/traduci.py "<cartella del gioco>" --luca       il protagonista si chiama Luca

<cartella del gioco> può essere la cartella del gioco o la sua sottocartella Archives.
Senza --luca il protagonista si chiama Bigby, come nell'originale.

Cosa fa:
  1. trova Archives e legge la versione del gioco (_res_game.version);
  2. per ognuno dei 6 archivi che la traduzione sostituisce, guarda se nel gioco c'è
     l'originale o quello tradotto, confrontando i testi con le frasi note di dati/:
     l'originale si salva in lavoro/originali (la copia precedente, se diversa, resta
     come .prec); per un archivio già tradotto serve la copia salvata prima, con gli
     stessi file dell'archivio del gioco a parte i testi tradotti;
  3. merge.py unisce dati/testi_2014.tsv, l'italiano nascosto nel gioco e dati/traduzioni.txt
     (risultato in lavoro/testi, con dettaglio.tsv: l'origine di ogni riga);
  4. build_mod.py crea i file da installare in lavoro/build;
  5. li copia nel gioco.
"""
import hashlib
import os
import shutil
import subprocess
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
from ttarch2 import Arch
from landb import Landb
from merge import load_testi, load_tsv, key, fix_mojibake, apply_names, NAMES
from installa import sha, MOD_FILES

RADICE = os.path.dirname(QUI)
TESTI_2014 = os.path.join(RADICE, 'dati', 'testi_2014.tsv')
TRADUZIONI = os.path.join(RADICE, 'dati', 'traduzioni.txt')
LAVORO = os.path.join(RADICE, 'lavoro')
ORIGINALI = os.path.join(LAVORO, 'originali')
TESTI = os.path.join(LAVORO, 'testi')
BUILD = os.path.join(LAVORO, 'build')

# archivi del gioco che build_mod.py ricrea con dentro i testi italiani dello slot inglese
SOSTITUITI = ['Fables_pc_%s_ar_data.ttarch2' % n
              for n in ('Boot', 'Fables101', 'Fables102', 'Fables103', 'Fables104', 'Fables105')]
TESTI_SLOT = ('boot_english.landb', 'ui_episode_english.landb', 'ui_credits_english.landb')

VERIFICA = ('Rimetti i file originali con la verifica del launcher (Steam: Libreria, tasto destro\n'
            'sul gioco > Proprietà > File installati > Verifica l\'integrità dei file di gioco)')


class Errore(Exception):
    pass


def trova_archives(percorso):
    p = os.path.abspath(percorso.strip().strip('"'))
    if os.path.isfile(p):       # trascinato l'eseguibile invece della cartella
        p = os.path.dirname(p)
    for c in (p, os.path.join(p, 'Archives')):
        if os.path.isfile(os.path.join(c, '_res_game.version')):
            return c
    raise Errore('In "%s" non trovo il gioco.\n'
                 'Indica la cartella di The Wolf Among Us Remastered, quella che contiene\n'
                 'TheWolfAmongUsRemastered.exe e la sottocartella Archives\n'
                 '(Steam: Libreria, tasto destro sul gioco > Gestisci > Sfoglia file locali).' % p)


def frasi_note():
    """Frasi inglesi e italiane conosciute (testi 2014 e traduzioni.txt), tolte quelle uguali."""
    t = load_testi(TESTI_2014)
    try:
        manual, forced = load_tsv(TRADUZIONI)
    except ValueError as e:
        raise Errore('%s\nCorreggi la riga in dati\\traduzioni.txt e rilancia.' % e)
    nostre = [v for v in list(manual.values()) + list(forced.values()) if v != '=']
    en = {key(e) for e, i in t.values()} | set(manual) | set(forced)
    it = {key(fix_mojibake(i)) for e, i in t.values()} | {key(v) for v in nostre}
    it |= {key(apply_names(s, n)) for s in list(it) for n in NAMES}    # con Bigby e con Luca
    comuni = en & it
    return en - comuni, it - comuni


def stato(path, frasi):
    """'originale', 'tradotto', 'illeggibile' o None se non si capisce: conta le righe dello
    slot inglese che sono frasi inglesi note e quelle che sono frasi italiane note."""
    en, it = frasi
    n_en = n_it = 0
    try:
        a = Arch(path)
        try:
            for e in a.files:
                if e[0].lower() in TESTI_SLOT:
                    L = Landb(e[0], a.read(e))
                    for x in L.entries:
                        t = key(L.dec(x.text))
                        if t:
                            n_en += t in en
                            n_it += t in it
        finally:
            a.f.close()
    except Exception:           # archivio rovinato o di formato sconosciuto
        return 'illeggibile'
    if n_it > n_en:
        return 'tradotto'
    if n_en > n_it:
        return 'originale'
    return None


def impronta(path):
    """nome -> hash di ogni file dell'archivio, tranne i testi dello slot inglese."""
    a = Arch(path)
    try:
        return {e[0].lower(): hashlib.sha1(a.read(e)).digest()
                for e in a.files if e[0].lower() not in TESTI_SLOT}
    finally:
        a.f.close()


def copia_valida(g, s, frasi):
    """True se s e' l'originale dell'archivio tradotto g: originale e con gli stessi file
    a parte i testi dello slot (una copia di un'altra versione del gioco non va bene)."""
    if not os.path.exists(s) or stato(s, frasi) != 'originale':
        return False
    try:
        return impronta(g) == impronta(s)
    except Exception:
        return False


def nel_lavoro(path):
    return os.path.abspath(path).startswith(os.path.abspath(LAVORO) + os.sep)


def permesso_negato(path):
    if nel_lavoro(path):
        return Errore('Non riesco a scrivere in %s.\n'
                      'Sposta la cartella del progetto in una cartella dove puoi scrivere\n'
                      '(non in Programmi), per esempio C:\\Traduzioni, e rilancia.' % LAVORO)
    return Errore('Non riesco a scrivere %s: chiudi il gioco e rilancia.' % path)


def copia(src, dst):
    """Copia passando da un file temporaneo: se si interrompe, dst resta com'era."""
    tmp = dst + '.tmp'
    try:
        shutil.copy2(src, tmp)
        os.replace(tmp, dst)
    except PermissionError:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise permesso_negato(dst)


def salva_originali(game, frasi):
    try:
        os.makedirs(ORIGINALI, exist_ok=True)
    except PermissionError:
        raise permesso_negato(ORIGINALI)
    for name in SOSTITUITI:
        g = os.path.join(game, name)
        s = os.path.join(ORIGINALI, name)
        if not os.path.isfile(g):
            raise Errore('Nel gioco manca %s.\n%s, poi rilancia.' % (name, VERIFICA))
        st = stato(g, frasi)
        if st == 'originale':
            if os.path.exists(s) and sha(s) == sha(g):
                continue
            if os.path.exists(s):
                os.replace(s, s + '.prec')
            copia(g, s)
            if sha(s) != sha(g):
                raise Errore('La copia di %s non coincide con l\'originale.' % name)
            print('  salvato l\'originale di %s' % name)
        elif st == 'tradotto':
            if not copia_valida(g, s, frasi):
                perche = ('la copia salvata in lavoro\\originali è di un\'altra versione del gioco'
                          if os.path.exists(s) else 'in lavoro\\originali non c\'è la sua copia originale')
                raise Errore('%s nel gioco è già tradotto e %s.\n%s, poi rilancia.'
                             % (name, perche, VERIFICA))
        elif st == 'illeggibile':
            raise Errore('%s nel gioco è rovinato o illeggibile.\n%s, poi rilancia.' % (name, VERIFICA))
        else:
            raise Errore('Non riesco a capire se %s è originale o tradotto:\n'
                         'forse il gioco ha cambiato formato. Vedi DOCUMENTAZIONE_TECNICA.md.' % name)


def lancia(passo, script, args):
    """Esegue uno degli script; il suo output si vede solo se qualcosa va storto."""
    print(passo)
    r = subprocess.run([sys.executable, '-I', '-X', 'utf8', os.path.join(QUI, script)] + args,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if r.returncode != 0:
        print(r.stdout.decode('utf-8', 'replace'))
        raise Errore('%s si è fermato con un errore (il dettaglio è qui sopra).\n'
                     'Se il gioco si è aggiornato, vedi DOCUMENTAZIONE_TECNICA.md.' % script)


def crea(game, nome):
    frasi = frasi_note()
    print('Controllo degli archivi del gioco...')
    salva_originali(game, frasi)
    # niente avanzi delle volte precedenti: un archivio vecchio in build verrebbe installato
    for d in (TESTI, BUILD):
        if os.path.isdir(d):
            shutil.rmtree(d)
    lancia('Unione dei testi...', 'merge.py',
           [game, TESTI_2014, TESTI, TRADUZIONI, '--originali', ORIGINALI, '--nome', nome])
    lancia('Creazione dei file della traduzione...', 'build_mod.py',
           [game, BUILD, TESTI, '--originali', ORIGINALI])
    fatti = sorted(os.listdir(os.path.join(BUILD, 'archivi')))
    if fatti != sorted(SOSTITUITI):
        raise Errore('build_mod.py ha creato archivi diversi da quelli attesi: %s.\n'
                     'Vedi DOCUMENTAZIONE_TECNICA.md.' % ', '.join(fatti))


def installa(game):
    print('Installazione...')
    for name in SOSTITUITI:
        copia(os.path.join(BUILD, 'archivi', name), os.path.join(game, name))
    for name in MOD_FILES:
        copia(os.path.join(BUILD, name), os.path.join(game, name))


def rimuovi(game):
    frasi = frasi_note()
    for name in MOD_FILES:
        p = os.path.join(game, name)
        if os.path.exists(p):
            try:
                os.remove(p)
            except PermissionError:
                raise permesso_negato(p)
            print('  cancellato %s' % name)
    mancano = []
    for name in SOSTITUITI:
        g = os.path.join(game, name)
        s = os.path.join(ORIGINALI, name)
        st = stato(g, frasi)
        if st == 'tradotto' and copia_valida(g, s, frasi):
            copia(s, g)
            print('  rimesso l\'originale di %s' % name)
        elif st in ('tradotto', 'illeggibile'):
            mancano.append(name)
    if mancano:
        raise Errore('Non ho una copia originale adatta di: %s.\n%s:\n'
                     'così la traduzione è tolta del tutto.' % (', '.join(mancano), VERIFICA))


def main():
    args = sys.argv[1:]
    opzioni = {a for a in args if a.startswith('--')}
    percorsi = [a for a in args if not a.startswith('--')]
    if len(percorsi) != 1 or opzioni - {'--rimuovi', '--solo-crea', '--luca'}:
        print(__doc__)
        return 2
    if sys.version_info < (3, 8):
        print('Serve Python 3.8 o successivo (questo è il %d.%d).' % sys.version_info[:2])
        return 1
    try:
        game = trova_archives(percorsi[0])
        versione = open(os.path.join(game, '_res_game.version'), encoding='latin-1').read().strip()
        print('Gioco:    %s' % game)
        print('Versione: %s' % versione)
        if '--rimuovi' in opzioni:
            rimuovi(game)
            print('\nFatto: la traduzione è stata tolta.')
            return 0
        nome = 'luca' if '--luca' in opzioni else 'bigby'
        print('Nome del protagonista: %s' % nome.capitalize())
        crea(game, nome)
        if '--solo-crea' in opzioni:
            print('\nFatto: i file sono in %s (non installati).' % BUILD)
            return 0
        installa(game)
    except Errore as e:
        print('\nERRORE: %s' % e)
        return 1
    except OSError as e:
        dove = e.filename or ''
        print('\nERRORE: non riesco a leggere o scrivere %s (%s).' % (dove, e.strerror or e))
        if dove and nel_lavoro(dove):
            print('Sposta la cartella del progetto in una cartella dove puoi scrivere\n'
                  '(non in Programmi), per esempio C:\\Traduzioni, e rilancia.')
        else:
            print('Chiudi il gioco e rilancia.')
        return 1
    print('\nFatto: traduzione installata.')
    print('Avvia il gioco; se i testi non sono in italiano: Opzioni > Language > Italiano.')
    print('L\'origine di ogni riga è in %s.' % os.path.join(TESTI, 'dettaglio.tsv'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
