<p align="center">
  <img src="img/logo_ita.png" alt="The Wolf Among Us Remastered con la bandiera italiana" width="640">
</p>

# The Wolf Among Us Remastered: traduzione italiana

Traduzione italiana amatoriale e gratuita di **The Wolf Among Us Remastered**, basata sulla traduzione
del 2014 del **CRYBIOLAB TEAM**. 🇮🇹

## Come installarla

Ci sono due modi. Scegline uno.

| | File pronti | Installazione automatica |
|-|-|-|
| Per chi | chi ha il gioco alla versione `PCS.18.3.7585` | tutti, anche dopo un aggiornamento del gioco |
| Cosa serve | niente | Python (gratuito) |
| Come | si copiano 8 file nella cartella del gioco | si trascina la cartella del gioco su `TRADUCI.bat` |
| Guida | [qui sotto](#file-pronti) | [FAI_DA_TE.md](FAI_DA_TE.md) |

La versione del gioco è scritta nel file `_res_game.version`, dentro la cartella `Archives` del gioco
(si apre con il Blocco note).

### File pronti

1. Chiudi il gioco.
2. Dall'ultima [Release](https://github.com/Link009/twau-remastered-ita/releases/latest) scarica uno
   dei due zip, a seconda di come vuoi che si chiami il protagonista:
   - `..._Bigby.zip`: **Bigby**, come nel gioco originale;
   - `..._Luca.zip`: **Luca**, il nome usato dalle traduzioni italiane.

   Poi estrailo (tasto destro sullo zip > Estrai tutto).
3. Apri la cartella `Archives` del gioco. Su Steam: Libreria, tasto destro sul gioco > Gestisci >
   Sfoglia file locali, poi la cartella `Archives`.
4. Salva da qualche parte una copia di questi 6 file originali (servono per disinstallare):
   - `Fables_pc_Boot_ar_data.ttarch2`
   - `Fables_pc_Fables101_ar_data.ttarch2`
   - `Fables_pc_Fables102_ar_data.ttarch2`
   - `Fables_pc_Fables103_ar_data.ttarch2`
   - `Fables_pc_Fables104_ar_data.ttarch2`
   - `Fables_pc_Fables105_ar_data.ttarch2`
5. Copia **tutti** gli 8 file della cartella `Archives` dello zip nella cartella `Archives` del gioco,
   sovrascrivendo quelli esistenti.
6. Avvia il gioco. Se i testi non sono in italiano: Opzioni > Language > **Italiano**.

Per disinstallare: cancella dalla cartella `Archives` del gioco `_resdesc_50_italiano.lua` e
`Fables_pc_italiano_ar_all.ttarch2`, poi rimetti i 6 file originali salvati (oppure usa la verifica
dei file del launcher: su Steam, tasto destro sul gioco > Proprietà > File installati >
Verifica l'integrità dei file di gioco).

### Installazione automatica

Serve se il gioco si è aggiornato, se vuoi correggere qualche frase o se preferisci non copiare
file a mano. In breve: installi Python, scarichi questo progetto e trascini la cartella del gioco
su `TRADUCI.bat`. Tutti i passaggi, uno per uno, sono in **[FAI_DA_TE.md](FAI_DA_TE.md)**.

## Crediti

### Traduzione originale (2014): CRYBIOLAB TEAM

| Ruolo | Nomi |
|-|-|
| Organizzazione | Crybio85 (Cristian), Puxxup (Fabrizio) |
| Traduzione e revisione | Puxxup, ClaySoft '65 (Claudio), Crybio85, Marco C., Giulia Manto, Peter Sanders, Lorz, Nelson |
| Revisione e beta test | Puxxup, UselessWhiskey |
| Font, archivi e installer | ClaySoft '65, Puxxup |

Un ringraziamento speciale al **Traduzione Twd Team (TTT)**.

Senza il loro lavoro questa traduzione non esisterebbe.

### Adattamento al Remastered

Link009

## Cosa contiene

| Origine del testo | Quota |
|-|-|
| Traduzione 2014 del CRYBIOLAB TEAM | circa 95% delle righe |
| Italiano ufficiale già presente nei file del Remastered, ma non attivabile dal gioco, uniformato ai nomi della traduzione 2014 | circa 2,5% (scene eliminate, scene ricreate, gallerie, schede del Libro delle Fiabe) |
| Traduzioni e correzioni nuove | circa 1,3% |

- Tutti i 5 episodi, i menu, gli obiettivi, gli extra e le schermate di avvio.
- Il protagonista si chiama **Bigby**, come nel gioco originale, oppure **Luca** (da LUpo CAttivo),
  il nome usato dalle traduzioni italiane: si sceglie durante l'installazione.
- Nomi e termini seguono la traduzione 2014: Neve, Miss Bianca, le Fiabe, i Terreni, la Malia,
  il Crooked Man, il Braccia Aperte, i Boschi, l'Ufficio Affari, il Pozzo delle Streghe.

## Note

- Il gioco non permette di aggiungere lingue, quindi l'italiano prende il posto dell'inglese
  (come nella traduzione del 2014): finché è installato l'inglese non è disponibile,
  francese, tedesco e spagnolo sì.
- La nota legale sotto i loghi iniziali resta in inglese: si trova in uno script cifrato del gioco.
- Nelle righe delle Impostazioni (QUALITÀ GRAFICA, SÌ/NO…) il gioco legge le lettere accentate con la
  codifica di Windows invece che con quella del resto del gioco: per questo quelle voci sono scritte in modo
  diverso e gli accenti escono giusti. Con Windows impostato in una lingua dell'Europa dell'Est, in greco o
  in cirillico, in quelle voci al posto delle lettere accentate possono comparire altre lettere.
- I file pronti valgono solo per la versione `PCS.18.3.7585` del gioco: su una versione diversa
  non vanno copiati. In quel caso usa l'installazione automatica.

## Segnalare errori

Apri una segnalazione nella sezione **Issues**, indicando la frase com'è nel gioco e, se puoi,
l'episodio e la scena. Se usi l'installazione automatica puoi anche correggerla da solo:
vedi "Correggere una frase" in [FAI_DA_TE.md](FAI_DA_TE.md).

## Per chi vuole sapere come funziona

- [DOCUMENTAZIONE_TECNICA.md](DOCUMENTAZIONE_TECNICA.md): formati dei file del gioco e funzionamento degli script.
- [AGENTS.md](AGENTS.md): istruzioni per chi si fa aiutare da un assistente IA.

## Versioni

| Versione | Data | Novità |
|-|-|-|
| 1.1 | 03/11/2026 | accenti corretti nelle Impostazioni (prima "SAOE", "QUALITÃÿ"); voci del menu troppo lunghe accorciate; scelta tra Bigby e Luca; pubblicati gli script, i testi 2014 e la guida per fare tutto da sé |
| 1.0 | 30/10/2026 | prima versione |

## Licenza

- **Script** (cartella `tools`, `TRADUCI.bat`, `RIMUOVI.bat`): licenza MIT, vedi [LICENSE](LICENSE).
- **Testi della traduzione** (cartella `dati`, file della cartella `Archives`): la traduzione 2014 è
  del CRYBIOLAB TEAM; l'adattamento è di Link009.
  Solo per uso personale e non commerciale; i diritti restano ai rispettivi autori.

## Avviso

Progetto amatoriale e gratuito, senza scopo di lucro e non affiliato a LCG Entertainment, Telltale,
Warner Bros. Games o DC. The Wolf Among Us, Fables e tutti i marchi citati appartengono ai rispettivi
proprietari. Per usare questa traduzione serve una copia originale del gioco.
