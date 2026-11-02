"""Installa o rimuove la traduzione italiana in The Wolf Among Us Remastered.

Uso: python -I installa.py <cartella Archives> <cartella build> <cartella backup> [--rimuovi]

Installa:
  - copia _resdesc_50_italiano.lua e Fables_pc_italiano_ar_all.ttarch2 (file nuovi);
  - per ogni archivio in <build>/archivi: salva l'originale in <backup> (solo se non c'e'
    gia' una copia, cosi' il backup resta sempre quello originale) e lo sostituisce.
Rimuovi:
  - cancella i due file della mod e rimette gli archivi originali dal backup.
"""
import hashlib
import os
import shutil
import sys

MOD_FILES = ['_resdesc_50_italiano.lua', 'Fables_pc_italiano_ar_all.ttarch2']


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def install(game, build, backup):
    os.makedirs(backup, exist_ok=True)
    ep_dir = os.path.join(build, 'archivi')
    for name in sorted(os.listdir(ep_dir)):
        orig = os.path.join(game, name)
        saved = os.path.join(backup, name)
        if not os.path.exists(saved):
            shutil.copy2(orig, saved)
            if sha(saved) != sha(orig):
                raise IOError('backup di %s non coincide' % name)
            print('backup:     %s' % name)
        shutil.copy2(os.path.join(ep_dir, name), orig)
        print('sostituito: %s' % name)
    for name in MOD_FILES:
        shutil.copy2(os.path.join(build, name), os.path.join(game, name))
        print('copiato:    %s' % name)


def remove(game, backup):
    for name in MOD_FILES:
        path = os.path.join(game, name)
        if os.path.exists(path):
            os.remove(path)
            print('rimosso:    %s' % name)
    for name in sorted(os.listdir(backup)):
        if name.endswith('.ttarch2'):
            shutil.copy2(os.path.join(backup, name), os.path.join(game, name))
            print('ripristinato: %s' % name)


def main():
    game, build, backup = sys.argv[1:4]
    if '--rimuovi' in sys.argv[4:]:
        remove(game, backup)
    else:
        install(game, build, backup)


if __name__ == '__main__':
    main()
