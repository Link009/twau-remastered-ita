@echo off
rem Toglie la traduzione: trascinare la cartella del gioco su questo file.
rem TRADUCI.bat e' uguale, cambiano solo AZIONE e TITOLO.
chcp 65001 >nul
setlocal
cd /d "%~dp0"
if exist "tools\traduci.py" goto :avvio
echo Questo file deve restare nella cartella del progetto, accanto alle cartelle tools e dati.
echo Estrai tutto lo zip (tasto destro, Estrai tutto) e usa i file della cartella estratta.
goto :fine

:avvio
set "AZIONE=--rimuovi"
set "TITOLO=Rimozione della traduzione italiana di The Wolf Among Us Remastered"

echo %TITOLO%
echo.
echo Prima di continuare chiudi il gioco.
echo.
set "GIOCO=%~1"
if defined GIOCO goto :python
echo Trascina la cartella del gioco sopra questo file, oppure incolla qui il suo percorso
echo (Steam: Libreria, tasto destro sul gioco, Gestisci, Sfoglia file locali).
echo.
set /p "GIOCO=Cartella del gioco: "
if not defined GIOCO goto :fine

:python
set "GIOCO=%GIOCO:"=%"
rem una barra finale unirebbe la virgoletta all'argomento dopo
if "%GIOCO:~-1%"=="\" set "GIOCO=%GIOCO:~0,-1%"
set "PY="
where py >nul 2>nul && set "PY=py -3"
if not defined PY (python --version >nul 2>nul && set "PY=python")
if defined PY goto :nome
echo.
echo Python non è installato. Scaricalo da https://www.python.org/downloads/
echo e durante l'installazione spunta "Add python.exe to PATH". Poi riprova.
goto :fine

:nome
rem solo TRADUCI.bat chiede il nome: in RIMUOVI.bat AZIONE e' gia' --rimuovi
if defined AZIONE goto :lancia
echo.
echo Come vuoi che si chiami il protagonista?
echo   B = Bigby, come nel gioco originale
echo   L = Luca, il nome usato dalle traduzioni italiane
set "NOME="
set /p "NOME=Scrivi B o L e premi Invio (solo Invio = Bigby): "
if /i "%NOME%"=="L" set "AZIONE=--luca"

:lancia
echo.
%PY% -I tools\traduci.py "%GIOCO%" %AZIONE%

:fine
echo.
pause
