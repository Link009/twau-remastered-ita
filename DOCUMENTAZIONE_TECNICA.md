# Documentazione tecnica

Come funziona la traduzione e come sono fatti i file del gioco. Tutto è verificato sulla versione
`PCS.18.3.7585` di The Wolf Among Us Remastered (ottobre 2026). Per installare basta
[FAI_DA_TE.md](FAI_DA_TE.md); questa pagina serve a chi vuole modificare gli script o adattarli
a una versione nuova del gioco.

## Come funziona la traduzione

| Punto | Spiegazione |
|-|-|
| L'italiano nascosto | Il Remastered contiene file `*_italian.landb` completi al 90%, ma il gioco non li fa scegliere: la lista delle lingue è fissa, negli script Lua cifrati. Aggiungere un set di lingua `italian` non la fa comparire, e se `prefs.prop` dice `italian` il gioco lo riporta a `english`. |
| Lo slot inglese | La traduzione prende il posto dell'inglese: i testi italiani vengono salvati come `*_english.landb`. Nel menu delle lingue la voce English diventa "Italiano". Con lo slot inglese anche la nota legale cifrata resta in inglese (con lo slot spagnolo usciva in spagnolo). |
| Il set "italiano" | `Fables_pc_italiano_ar_all.ttarch2` + `_resdesc_50_italiano.lua` (copia di quello spagnolo con nome `italiano`, priorità 900, `enableMode = "constant"`): sta sopra i set delle lingue (800) e degli episodi (20-25), quindi i suoi file vincono. |
| Gli archivi sostituiti | Alcuni testi il set non li può coprire: `boot_*.landb` (letto prima che i set siano attivi) e `ui_episode_*`, `ui_credits_*` (diversi in ogni episodio, con lo stesso nome). Per questi si ricreano gli archivi del gioco `Fables_pc_Boot_ar_data` e `Fables_pc_Fables101..105_ar_data` uguali agli originali tranne quei file. |
| I testi | Per ogni riga, in ordine: correzione forzata di `traduzioni.txt`, traduzione 2014, traduzione manuale di `traduzioni.txt`, italiano ufficiale nascosto, inglese. Poi un solo nome per il protagonista (Bigby, oppure Luca con `--luca`) in tutte le righe tradotte, tranne i crediti che elencano i personaggi con il nome originale ("BIGBY WOLF"); si rimettono i tag `{..}` dell'inglese se mancano; le voci delle righe delle Impostazioni si scrivono in cp1252 (vedi sotto, "Codifica delle Impostazioni"). |

## Struttura del progetto

| Percorso | Contenuto |
|-|-|
| `TRADUCI.bat`, `RIMUOVI.bat` | trovano Python e lanciano `tools\traduci.py` (con `--rimuovi` il secondo) |
| `tools\traduci.py` | il comando unico: salva gli originali, unisce i testi, crea i file, installa |
| `tools\merge.py` | unisce traduzione 2014, italiano ufficiale nascosto e `traduzioni.txt` |
| `tools\build_mod.py` | crea il set "italiano" e gli archivi sostituiti |
| `tools\installa.py` | installazione e rimozione semplici, senza controlli (per uso manuale) |
| `tools\esporta_2014.py` | crea `dati\testi_2014.tsv` dal pack originale del 2014 |
| `tools\ttarch2.py`, `tools\landb.py` | lettura e scrittura degli archivi e dei testi del gioco |
| `dati\testi_2014.tsv` | la traduzione 2014 del CRYBIOLAB TEAM: chiave, inglese 2014, italiano |
| `dati\traduzioni.txt` | traduzioni nuove e correzioni (formato nel file stesso) |
| `Archives\` | i file pronti per la versione `PCS.18.3.7585` |
| `lavoro\` | creata da `traduci.py`, non sta nel repository: `originali\` (archivi originali del gioco), `testi\` (risultato di `merge.py`), `build\` (file da installare) |

Requisiti: Python 3.8 o successivo, nessuna libreria esterna.

## Comandi

`traduci.py` (da qualsiasi cartella, a gioco chiuso):

```
python -I tools\traduci.py "<cartella del gioco>"              crea e installa
python -I tools\traduci.py "<cartella del gioco>" --rimuovi    toglie la traduzione
python -I tools\traduci.py "<cartella del gioco>" --solo-crea  crea in lavoro\build senza installare
python -I tools\traduci.py "<cartella del gioco>" --luca       il protagonista si chiama Luca (senza: Bigby)
```

Gli stessi passi a mano, dalla cartella `tools` (`<GIOCO>` è la cartella `Archives` del gioco,
`<ORIGINALI>` una cartella con i 6 archivi originali, necessaria se nel gioco sono già tradotti):

```
python -I merge.py "<GIOCO>" ..\dati\testi_2014.tsv ..\lavoro\testi ..\dati\traduzioni.txt --originali <ORIGINALI> [--nome luca]
python -I build_mod.py "<GIOCO>" ..\lavoro\build ..\lavoro\testi --originali <ORIGINALI>
python -I installa.py "<GIOCO>" ..\lavoro\build <ORIGINALI>
```

`merge.py` scrive in `lavoro\testi` anche `report.txt` (statistiche e righe di `traduzioni.txt` mai usate:
di solito l'inglese scritto in modo diverso da quello del gioco), `dettaglio.tsv` (origine di ogni riga)
e `da_tradurre.tsv` (frasi rimaste in inglese).

### Come `traduci.py` riconosce un archivio tradotto
Confronta i testi dello slot inglese (`boot_english`, `ui_episode_english`, `ui_credits_english`)
con le frasi note: inglesi e italiane di `testi_2014.tsv` e di `traduzioni.txt`, tolte quelle uguali
nelle due lingue. Più frasi italiane che inglesi: tradotto; il contrario: originale. Sulla versione
`PCS.18.3.7585` il margine è netto (per esempio Fables101: 163 inglesi e 0 italiane nell'originale,
1 e 164 nel tradotto; Boot: 5 e 0 contro 0 e 5).

- Archivio originale nel gioco: viene copiato in `lavoro\originali` (la copia precedente, se diversa, diventa `.prec`).
- Archivio tradotto: serve la copia originale già salvata, con gli stessi file dell'archivio del gioco a parte
  i testi dello slot (confronto file per file): una copia di un'altra versione del gioco non viene usata.
  Altrimenti lo script si ferma senza toccare il gioco.
- Archivio illeggibile: lo script si ferma e chiede la verifica dei file del launcher.
- `--rimuovi` rimette solo gli archivi tradotti, e solo con una copia adatta; quelli già originali
  (per esempio dopo un aggiornamento) restano.
- Prima di ogni creazione `lavoro\testi` e `lavoro\build` vengono svuotate; le copie nel gioco passano da
  un file `.tmp`, così un'interruzione non lascia un archivio a metà.

## Formato degli archivi `.ttarch2` (TTA4)

| Parte | Formato |
|-|-|
| NCTT (non compresso, archivi delle lingue) | `"NCTT"` + u64 dimensione del contenuto + contenuto |
| ZCTT (compresso, archivi `_data`) | `"ZCTT"` + u32 dimensione blocco (`0x10000`) + u32 numero blocchi + u64 offset[n+1] + blocchi deflate raw; contenuto riempito a zeri fino a un multiplo di `0x10000` |
| Contenuto | `"4ATT"` + u32 dimensione tabella nomi (multiplo di `0x10000`) + u32 numero file + voci + tabella nomi + dati |
| Voce (28 byte) | u64 CRC64 del nome + u64 offset (dall'inizio dei dati) + u32 dimensione + u32 0 + u16 blocco nome + u16 offset nome |
| CRC64 | ECMA-182 (poly `0x42F0E1EBA9EA3693`, init 0, non riflesso) sul nome in minuscolo |
| Ordine | voci ordinate per CRC64; nomi e dati in ordine alfabetico (minuscolo), senza padding |
| 2014 (TTA3) | `"3ATT"` + u32 2, poi come TTA4 |

`write_archive` ricrea gli archivi del gioco con contenuto identico byte per byte (per ZCTT la
compressione usa zlib livello 9: diversa dall'originale ma valida).

## Formato dei testi `.landb`

| Parte | Formato |
|-|-|
| Versione | MSV6 = Remastered (UTF-8), MSV5 = 2014 (cp1252) |
| Header | magic + u32 dimensione sezione principale + u32 dimensione sezione asincrona + u32 0 + u32 n classi + n×12 byte |
| Mappa | 16 byte (`08 00 00 00 x 08 00 00 00 y`) + u32 dimensione blocco + u32 numero righe |
| Riga | u32 chiave + 52 byte fissi + u32 dimensione blocco {nome personaggio `[u32 dim][u32 len][byte]`, testo idem, flags (blocco da 8)} + 12 byte (MSV6) o 4 byte (MSV5) |
| Coda | registro dei file `.lang` per riga, diverso per file: si copia com'è |
| Scrittura | si ricalcolano le dimensioni dei blocchi e la dimensione della sezione principale |
| Inglese e italiano | stesse chiavi, stesso ordine, stessi campi; cambia solo `flags` (inglese `0x01`, tradotto `0x12`) |
| Tag | `{angrya}` animazione o espressione, `[pickup4]` indicazione per i doppiatori; righe fatte solo di `[...]` = scelte d'azione mostrate al giocatore oppure suoni |

La chiave di una riga è stabile tra il gioco del 2014 e il Remastered: è così che la traduzione 2014
si ritrova riga per riga.

## Il gioco

| Chiave | Valore | Note |
|-|-|-|
| Cartella dati | `<installazione>\Archives` | archivi `.ttarch2` + file `_resdesc_50_<set>.lua` |
| Versione | `Archives\_res_game.version` | |
| `_resdesc_50_<set>.lua` | Lua in chiaro, uno per "resource set" | campi usati: `name`, `priority`, `enableMode`, `gameDataArchives` |
| Priorità dei set | Project -8888, Boot 10, Menu 10, Fables101-105 20, ReFables101-105 25, french/german/spanish 800, italiano 900 | a parità di nome file vince la priorità più alta |
| `enableMode` | `constant` (sempre attivo), `bootable` (episodi), `localization` (lingue) | |
| Lingua scelta | `Documenti\Telltale Games\The Wolf Among Us Remastered\prefs.prop`, chiave `Game Language` | `english`/`french`/`german`/`spanish` |
| Script Lua | cifrati (iniziano con `\x1bLEn`) | es. `bootTitle.lua`, con la nota legale della schermata dei loghi |
| Voci del menu lingue | english `0x15433332`, `0x15433051`, `0x1543311f` | in `ui_menu_<lingua>.landb`; `build_mod.py` le rinomina "Italiano" |
| Font | i font principali hanno tutte le vocali accentate, maiuscole comprese | nessun font da aggiungere |

## Testi 2014: `dati\testi_2014.tsv`

Il pack 2014 del CRYBIOLAB TEAM conteneva archivi interi del gioco di allora, con l'italiano dentro i
`*_english.landb` (il gioco era solo in inglese). Di quel pack servono solo i testi, quindi
`esporta_2014.py` li ha scritti in un file di testo:

- una riga per chiave: chiave esadecimale, inglese del 2014, italiano; le righe con `#` e l'intestazione si saltano;
- a capo, tabulazioni e barre rovesciate scritti come `\n`, `\t`, `\\`;
- l'ordine conta: a parità di frequenza `merge.py` sceglie la traduzione che compare prima;
- il testo è quello del pack, comprese 2 righe con la codifica rovinata (`PiÃ¹`), che `merge.py` corregge in lettura.

`merge.py` accetta sia il file sia la cartella del pack originale, con risultato identico byte per byte.

## Unione dei testi (`merge.py`), versione 1.1

| Origine | Righe | Regola |
|-|-|-|
| correzione | 4 | `! ` in `traduzioni.txt`, vince su tutto (voci del menu accorciate) |
| crediti_team | 4 | crediti del team 2014 + crediti Telltale attuali |
| amatoriale | 23.821 | stessa chiave e stesso inglese del 2014 |
| amatoriale_simile | 16 | stessa chiave, inglese simile al 90% o più |
| amatoriale_testo | 1.311 | stessa frase inglese (3+ parole) tradotta altrove nel 2014 |
| amatoriale_breve | 303 | frase breve con un'unica traduzione 2014 |
| manuale / mantenuta | 256 / 101 | `traduzioni.txt` (`=` lascia l'inglese) |
| ufficiale | 653 | italiano ufficiale nascosto |
| inglese | 319 | segnaposto, nomi di file, note, suoni, nomi nei crediti |
| vuote | 283 | righe senza testo |

## Se il gioco si aggiorna

1. Rilanciare `traduci.py`: di solito basta. Gli archivi rimessi originali dall'aggiornamento vengono salvati
   di nuovo, quelli non toccati restano tradotti e si usa la copia salvata prima.
2. Se `merge.py` o `build_mod.py` si fermano, il gioco ha cambiato qualcosa. Dove guardare:
   - errore nella lettura di un archivio: è cambiato il formato `.ttarch2` (`ttarch2.py`);
   - `parse finito a ... atteso ...`: è cambiato il formato `.landb` (`landb.py`);
   - `righe diverse tra italiano e english`: i file `*_italian` e `*_english` non hanno più le stesse chiavi;
   - `voce 0x... non trovata`: sono cambiate le chiavi del menu lingue (`LABELS` in `build_mod.py`);
   - archivi creati diversi da quelli attesi: sono cambiati i file per episodio (`SOSTITUITI` in `traduci.py`).
3. Molte righe di `traduzioni.txt` "mai usate" in `lavoro\testi\report.txt` vogliono dire che l'inglese del gioco è cambiato.

## Limiti noti

| Limite | Motivo |
|-|-|
| La nota legale sotto i loghi resta in inglese | sta in `bootTitle.lua`, cifrato |
| L'inglese non è disponibile con la traduzione installata | il gioco non accetta lingue nuove |
| Voci delle Impostazioni con Windows in alfabeti diversi | sono scritte in cp1252 (vedi "Codifica delle Impostazioni"): con una codifica di Windows diversa (Europa dell'Est, greco, cirillico) al posto delle lettere accentate possono comparire altre lettere |

## Codifica delle Impostazioni

Le righe delle Impostazioni (etichetta a sinistra, valore a destra, per esempio QUALITÀ GRAFICA ◄ ALTA ►)
il gioco le legge con la codifica di Windows (cp1252), non in UTF-8 come il resto dei testi: scritte in
UTF-8, "QUALITÀ" esce "QUALITÃÿ" e "SÌ" esce "SÃŒ" (segnalato come "SAOE"). Succede anche con l'italiano
ufficiale nascosto. I font hanno tutte le lettere accentate; la lettura sbagliata avviene negli script
cifrati, quindi non si corregge alla fonte.

Verifica nel gioco (03/11/2026, con una build che mostrava davanti a ogni voce le ultime cifre della sua chiave):

| Dove | Codifica letta | Voci |
|-|-|-|
| Etichette delle righe delle Impostazioni | cp1252 | `1543311b` QUALITÀ GRAFICA, `1543313d` QUALITÀ TEXTURE, `1543331c` MODALITÀ NOIR (viste); `15433135` QUALITÀ OMBRE, `1543310f` MODALITÀ MINIMALE, `15433108` LUMINOSITÀ, `15433125` SENSIBILITÀ MOUSE (stesso gruppo, non mostrate su PC) |
| Valori delle righe | cp1252 | `15433129` SÌ (vista), `15433183` SÌ |
| Pagina principale delle Impostazioni | UTF-8 | `15433119` GIOCABILITÀ |
| Titoli delle schermate | UTF-8 | `15433083` GIOCABILITÀ |
| Finestre di dialogo e pulsanti | UTF-8 | `15433147` SÌ (Abbandona gioco) |
| Schede degli episodi, sottotitoli | UTF-8 | |

`merge.py` scrive in cp1252 le voci di `MENU_CP1252` e tutte le altre in UTF-8. Se una voce nuova delle
Impostazioni mostra "Ã" seguito da un altro carattere, la sua chiave va aggiunta a `MENU_CP1252`.
