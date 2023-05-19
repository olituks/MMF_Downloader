# MMF_Downloader
A simple MyMiniFactory mass downloader

If, like me, you are frustrated by the lack of a simple and efficient way to download your files from MyMiniFactory each month, here's a Python program that should make your life easier.

MMF_Downloader or MMFD allows you to:

- Browse the pages of available objects starting from a specific URL.
- Extract detailed information for each object into a SQLite database.
- Download the archive files for each object.
- That's all for now, more features will come later :)

I want to clarify that this code does not allow you to pirate or download archives from MyMiniFactory that you haven't paid for or that are not shared with you. This code is intended to create a backup of your miniatures in case MyMiniFactory disappears.

In the my_settings.py file, please appropriately change the values:
- default_download_path = "chrome download files path//" # make sure to finish the path with // (NFS mount is working)
- login = "your login"
- pwd = "your password"
- sqlite_db_name = "the target path for the SQLite DB file"

  Regarding Python libraries, you will need to install any missing ones.
  Don't forget to properly set the my_settings_file.py. The file contains the global variables.

## Les détails en Français:
Si, comme moi, vous êtes frustré de ne pas pouvoir télécharger facilement et efficacement vos fichiers sur MyMiniFactory chaque mois, voici un programme écrit en Python qui devrait vous faciliter la vie.

MMF_Downloader, également connu sous le nom de MMFD, vous permet de :

- Parcourir les pages d'objets disponibles à partir d'une URL spécifique.
- Extraire les informations détaillées de chaque objet et les enregistrer dans une base de données SQLite.
- Télécharger les fichiers d'archives de chaque objet.
- C'est tout pour le moment, d'autres fonctionnalités viendront ultérieurement :)

Je tiens à préciser que ce code ne permet pas de pirater ou de télécharger des archives de MyMiniFactory que vous n'avez pas payées ou qui ne sont pas partagées avec vous. Ce code vous permet simplement de sauvegarder vos miniatures au cas où MyMiniFactory viendrait à disparaître.

Dans le fichier my_settings.py, veuillez modifier les valeurs correspondantes :
- default_download_path = "chemin cible pour les fichiers téléchargés par Chrome//" # assurez-vous de terminer le chemin par // (mount NFS validé)
- login = "votre identifiant"
- pwd = "votre mot de passe"
- sqlite_db_name = "le chemin cible pour le fichier de base de données SQLite"

En ce qui concerne les bibliothèques Python, veuillez installer celles qui vous manquent :)
N'oubliez pas de remplir correctement le fichier my_setting_file.py. Ce fichier contient les variables globales de l'application.
