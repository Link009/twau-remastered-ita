# Istruzioni per assistenti IA

Questo file è per un assistente IA che aiuta qualcuno a usare o modificare la traduzione italiana di
The Wolf Among Us Remastered. Parla con l'utente in italiano e in modo semplice: spesso non è un programmatore.

## Il progetto in breve

- Il gioco ha un italiano ufficiale nascosto ma non selezionabile; la traduzione prende il posto
  dell'inglese ("slot" inglese). Dettagli in `DOCUMENTAZIONE_TECNICA.md`: leggilo prima di toccare il codice.
- I testi vengono da `dati/testi_2014.tsv` (traduzione 2014 del CRYBIOLAB TEAM), dall'italiano nascosto
  nel gioco e da `dati/traduzioni.txt` (traduzioni nuove e correzioni).
- `tools/traduci.py` fa tutto: salva gli originali del gioco in `lavoro/originali`, unisce i testi
  (`merge.py`), crea i file (`build_mod.py`), li installa. `TRADUCI.bat` e `RIMUOVI.bat` lo lanciano.
- Solo Python 3.8+ e libreria standard. Lancia gli script con `python -I` (o `py -3 -I`).

## Regole

1. **Il gioco deve essere chiuso** quando si installa o si toglie la traduzione.
2. **Non cancellare né sovrascrivere `lavoro/originali`**: sono gli unici originali dei 6 archivi
   modificati, a meno di una verifica dei file dal launcher.
3. **Non modificare i file del gioco a mano**: passa sempre da `traduci.py`, che salva gli originali e
   controlla lo stato di ogni archivio. Per le prove usa `--solo-crea` (crea in `lavoro/build` senza installare)
   o una copia della cartella `Archives` fuori dal gioco.
4. **Prima di installare, chiedi conferma all'utente** e spiega cosa cambia nel gioco.
5. **Le correzioni di testo vanno in `dati/traduzioni.txt`**, non nel codice e non in `testi_2014.tsv`
   (il TSV è il lavoro del team 2014: resta com'è).
6. **Se cambi `merge.py`, `build_mod.py`, `landb.py` o `ttarch2.py` senza voler cambiare il risultato**,
   verifica che l'output sia identico byte per byte a prima: salva `lavoro/testi` e `lavoro/build`,
   rifai con `--solo-crea`, confronta ogni file.
7. Mantieni lo stile degli script: commenti in italiano, nessuna libreria esterna, nessuna emoji nel codice.

## Compiti frequenti

### Installare o togliere
`python -I tools/traduci.py "<cartella del gioco>"`, oppure con `--rimuovi`. Se lo script si ferma,
il messaggio dice cosa fare; la tabella "Se qualcosa non va" di `FAI_DA_TE.md` copre i casi comuni.

### Correggere una frase
1. Trova la riga in `lavoro/testi/dettaglio.tsv` (colonne: archivio, file, chiave, origine, inglese, italiano).
2. Aggiungi in fondo a `dati/traduzioni.txt`: `! <inglese esatto> ==> <italiano>`. I tag `{..}` e `[..]`
   dell'inglese si possono omettere; `\n` va a capo. La correzione vale per tutte le righe con lo stesso inglese.
3. Rilancia `traduci.py` e controlla in `lavoro/testi/dettaglio.tsv` che la riga abbia origine `correzione`.
4. Rispetta il glossario in testa a `dati/traduzioni.txt` (Bigby e non Luca, Neve, Fiabe, Terreni, Malia...).

### Il gioco si è aggiornato
1. Leggi la versione in `Archives/_res_game.version` del gioco.
2. Rilancia `traduci.py`: di solito basta.
3. Se si ferma, segui "Se il gioco si aggiorna" in `DOCUMENTAZIONE_TECNICA.md`. Lavora con `--solo-crea`
   finché la creazione non riesce, poi chiedi all'utente di provare il gioco: menu, inizio dell'episodio 1,
   una scena con scelte, un riassunto "Nei precedenti episodi", i crediti.
4. Controlla `lavoro/testi/report.txt`: le righe di `traduzioni.txt` "mai usate" indicano un inglese cambiato;
   `lavoro/testi/da_tradurre.tsv` elenca le frasi rimaste in inglese.

## Da sapere

- I file della cartella `Archives/` del repository sono pronti per la sola versione `PCS.18.3.7585`.
- La nota legale sotto i loghi iniziali resta in inglese (script cifrato): non è un errore da correggere.
- Le righe delle Impostazioni il gioco le legge in cp1252: le voci di `MENU_CP1252` in `merge.py` sono scritte
  così apposta (in UTF-8 uscirebbero "QUALITÃÿ", "SÃŒ"). Dettagli e voci verificate in "Codifica delle
  Impostazioni" di `DOCUMENTAZIONE_TECNICA.md`. Non convertirle in UTF-8.
- Lo spazio nel menu è poco: una voce più lunga dell'originale può finire sotto le frecce o essere tagliata.
  Dopo aver cambiato una voce del menu, chiedi all'utente uno screenshot della schermata.
- Il protagonista si chiama Bigby, oppure Luca con `--luca` (`TRADUCI.bat` lo chiede). Le correzioni in
  `traduzioni.txt` si scrivono con "Bigby": in modalità Luca il nome viene cambiato in automatico.
