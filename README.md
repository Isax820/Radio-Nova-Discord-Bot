# Radio Nova Discord Bot (simple)

Petit bot Python pour joindre un canal vocal Discord et y diffuser un flux radio (Radio Nova).

Prérequis
- Python 3.8+
- ffmpeg installé et présent dans le PATH (Windows: ajoute le dossier contenant ffmpeg.exe à ta variable d'environnement PATH).

Installation

1. Ouvre PowerShell et place-toi dans le dossier du projet:

```powershell
cd "C:\Users\isaie\Documents\Créations\Code\radio-nova-discord-bot"
```

2. Crée un environnement virtuel (optionnel) et installe les dépendances:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

3. Copie le fichier d'exemple et modifie les valeurs:

```powershell
copy .env.example .env
# Édite .env et mets ton token Discord et l'URL de stream Radio Nova
```

Note: je n'ai pas inclus ici d'URL officielle du flux Radio Nova par défaut — remplace `STREAM_URL` par une URL de flux MP3/OGG valide pour Radio Nova si tu en as une.

Utilisation

1. Lance le bot:

```powershell
python bot.py
```

2. Dans Discord, invite le bot avec les permissions `Connect` et `Speak`. Ensuite, depuis un canal texte du serveur où le bot est présent:

- `!join` : fait rejoindre le bot au canal vocal où tu te trouves
- `!playnova` : démarre la lecture du flux configuré
- `!stop` : arrête la lecture
- `!pause` / `!resume` : pause et reprend
- `!leave` : déconnecte le bot
- `!volume <0.0-2.0>` : ajuste le volume

Dépannage
- Si le bot dit qu'il ne peut pas lire le flux, vérifie que `STREAM_URL` est accessible et qu'`ffmpeg` est correctement installé.
- Vérifie que le bot a les permissions vocales sur ton serveur.

Améliorations possibles
- Détecter automatiquement une URL de flux officielle de Radio Nova (requiert recherche et validation)
- Ajouter une petite interface web pour contrôler la lecture
