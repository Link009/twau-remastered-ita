# Installare la traduzione da soli

Questa guida spiega come creare e installare la traduzione sul proprio gioco con un doppio clic.
Funziona con qualsiasi versione del gioco, anche dopo un aggiornamento, e permette di correggere
le frasi che non piacciono.

Ci vogliono circa 10 minuti la prima volta, poi meno di un minuto.

## Cosa serve

- **The Wolf Among Us Remastered** per PC, installato.
- **Python**, un programma gratuito che fa funzionare gli script della traduzione.
- **Questo progetto**, scaricato da GitHub.

## 1. Installare Python (solo la prima volta)

1. Vai su https://www.python.org/downloads/ e premi il pulsante giallo **Download Python**.
2. Apri il file scaricato.
3. Se nella prima schermata c'è la casella **Add python.exe to PATH**, spuntala.
4. Premi **Install Now** e aspetta la fine.

Se Python è già installato (versione 3.8 o successiva) puoi saltare questo passo.

## 2. Scaricare il progetto

1. Apri la pagina principale del progetto, https://github.com/Link009/twau-remastered-ita,
   premi il pulsante verde **Code** e poi **Download ZIP**.
   Non usare lo zip della sezione Release: contiene solo i file pronti, senza gli script.
2. Trova lo zip scaricato (di solito nella cartella Download), tasto destro > **Estrai tutto** > **Estrai**.
3. Si apre la cartella `twau-remastered-ita-main`, che contiene `TRADUCI.bat`, `RIMUOVI.bat`
   e le cartelle `tools`, `dati`, `Archives`. Puoi spostarla dove vuoi, tranne che in Programmi.

Usa sempre la cartella estratta, non lo zip: dall'interno dello zip i file non funzionano.

## 3. Trovare la cartella del gioco

Su Steam: Libreria, tasto destro su **The Wolf Among Us Remastered** > **Gestisci** > **Sfoglia file locali**.

Si apre la cartella che contiene `TheWolfAmongUsRemastered.exe` e la sottocartella `Archives`:
è quella giusta. Lasciala aperta.

## 4. Installare la traduzione

1. **Chiudi il gioco.**
2. Trascina la cartella del gioco sopra `TRADUCI.bat`. In alternativa:
   - fai doppio clic su `TRADUCI.bat`;
   - nella finestra del gioco clicca sulla barra dell'indirizzo in alto, copia il percorso (Ctrl+C);
   - torna nella finestra nera, incolla il percorso con Ctrl+V e premi Invio.
3. Lo script chiede come vuoi che si chiami il protagonista:
   - premi **Invio** (oppure scrivi `B` e premi Invio) per **Bigby**, come nel gioco originale;
   - scrivi `L` e premi Invio per **Luca**, il nome usato dalle traduzioni italiane.

   Puoi cambiare idea quando vuoi: basta rifare il passo 4 e scegliere l'altro nome.
4. Aspetta qualche secondo. Se va tutto bene, alla fine c'è scritto:

   ```
   Fatto: traduzione installata.
   ```

5. Premi un tasto per chiudere la finestra.
6. Avvia il gioco. Se i testi non sono in italiano: Opzioni > Language > **Italiano**.

La prima volta lo script salva una copia dei 6 file del gioco che modifica nella cartella
`lavoro\originali` del progetto. **Non cancellare la cartella `lavoro`**: serve per togliere la
traduzione e per rifarla dopo una correzione.

**Se Windows chiede conferma** prima di aprire `TRADUCI.bat`: succede con i file scaricati da internet.
Se compare "Windows ha protetto il PC", premi **Ulteriori informazioni** e poi **Esegui comunque**;
se compare un avviso di sicurezza, premi **Esegui**.

## Togliere la traduzione

Chiudi il gioco e trascina la cartella del gioco sopra `RIMUOVI.bat` (oppure doppio clic e
incolla il percorso, come sopra). Il gioco torna com'era.

## Dopo un aggiornamento del gioco

Un aggiornamento può rimettere alcuni file originali e togliere in parte la traduzione.
Basta rifare il passo 4: lo script salva i file nuovi e ricrea la traduzione per la nuova versione.

Se lo script si ferma con un errore, vedi più in basso "Se qualcosa non va".

## Correggere una frase

Ogni frase del gioco ha una riga nel file `lavoro\testi\dettaglio.tsv`, che lo script crea al passo 4.

1. Apri `lavoro\testi\dettaglio.tsv` con il Blocco note. Ogni riga ha 6 colonne, separate da
   tabulazioni che nel Blocco note sembrano spazi: archivio, file, chiave, origine, **inglese**, **italiano**.
2. Cerca la frase italiana com'è nel gioco (Ctrl+F).
3. Copia il testo inglese della stessa riga, la penultima colonna, esattamente com'è.
4. Apri `dati\traduzioni.txt` con il Blocco note e aggiungi in fondo una riga così:

   ```
   ! testo inglese ==> nuova traduzione italiana
   ```

   Per esempio:

   ```
   ! Fuck off, Bufkin. ==> Vaffanculo, Bufkin.
   ```

   - `! ` all'inizio (punto esclamativo e spazio) fa vincere la tua traduzione su tutte le altre;
   - tra le due parti va ` ==> ` (spazio, uguale, due maggiore, spazio);
   - i pezzi dell'inglese tra parentesi `{ }` e `[ ]` si possono lasciare fuori;
   - per andare a capo nella frase italiana scrivi `\n`;
   - la correzione vale per tutte le frasi del gioco con lo stesso testo inglese.
5. Salva il file e rifai il passo 4.

Se la correzione può servire anche agli altri, segnalala nella sezione **Issues** del progetto su GitHub.

## Se qualcosa non va

| Messaggio | Cosa fare |
|-|-|
| `deve restare nella cartella del progetto` | Hai aperto il `.bat` da dentro lo zip o lo hai spostato: rifai il passo 2 e usa i file della cartella estratta. |
| `Python non è installato` | Rifai il passo 1, spuntando **Add python.exe to PATH**, poi chiudi e riapri la finestra. |
| `non trovo il gioco` | Hai indicato una cartella sbagliata: rifai il passo 3. |
| `chiudi il gioco e rilancia` | Il gioco è aperto: chiudilo e rifai il passo 4. |
| `Non riesco a scrivere in ...\lavoro` | La cartella del progetto è in un posto protetto (per esempio Programmi): spostala, per esempio in `C:\Traduzioni`, e rifai il passo 4. |
| `è già tradotto e in lavoro\originali non c'è la sua copia originale` | La traduzione era già installata, per esempio copiando i file pronti, e lo script non ha gli originali. Se li avevi salvati, copia i 6 file `.ttarch2` nella cartella `lavoro\originali` del progetto; altrimenti usa la verifica dei file di Steam (tasto destro sul gioco > Proprietà > File installati > Verifica l'integrità dei file di gioco). Poi rifai il passo 4. |
| `la copia salvata in lavoro\originali è di un'altra versione del gioco` oppure `è rovinato o illeggibile` | Usa la verifica dei file di Steam (come sopra) e rifai il passo 4. |
| `traduzioni.txt, riga ...: manca " ==> "` | Una riga che hai aggiunto a `dati\traduzioni.txt` è scritta male: correggila come spiegato in "Correggere una frase". |
| `Non riesco a capire se ... è originale o tradotto` oppure `si è fermato con un errore` | Probabilmente un aggiornamento del gioco ha cambiato il formato dei file. Apri una segnalazione nella sezione **Issues** e incolla tutto il testo della finestra. |

## Farsi aiutare da un assistente IA

Se usi un assistente IA che può leggere e modificare i file sul tuo computer, aprigli la cartella del
progetto e chiedigli di leggere `AGENTS.md`: lì ci sono il contesto e le regole per lavorare sulla
traduzione senza rovinare il gioco. Per i dettagli tecnici c'è `DOCUMENTAZIONE_TECNICA.md`.
