@echo off
SET MODE=%1

REM Vérification du mode passé en argument
IF NOT "%MODE%"=="init" IF NOT "%MODE%"=="check" (
  echo Usage: launch.cmd [init^|check]
  exit /b 1
)

REM Création de l’environnement virtuel s’il n’existe pas déjà
IF NOT EXIST venv (
  echo 📦 Création de l'environnement virtuel...
  python -m venv venv
)

REM Activation de l’environnement virtuel
echo ⚙️  Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Mise à jour de pip
echo 🔄 Mise à jour de pip...
python -m pip install --upgrade pip

REM Installation des dépendances
echo 📚 Installation des dépendances...
pip install -r requirements.txt

REM Lancement du script Python principal
echo 🚀 Lancement de main.py avec le mode '%MODE%'...
python main.py %MODE%
