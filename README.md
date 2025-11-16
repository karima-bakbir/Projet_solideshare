# SolidShare

SolidShare est une application web Flask pour la gestion d'entraide solidaire au sein de groupes. Elle permet aux utilisateurs de créer des groupes, de demander de l'aide financière et de contribuer aux demandes des autres membres.

## Fonctionnalités

- **Gestion des utilisateurs** : Inscription, connexion et authentification
- **Création de groupes** : Les utilisateurs peuvent créer et rejoindre des groupes d'entraide
- **Demandes d'aide** : Soumettre des demandes d'aide financière avec titre, description et montant
- **Contributions** : Contribuer anonymement ou publiquement aux demandes
- **Suivi des remboursements** : Système de suivi des remboursements
- **Messages de remerciement** : Envoyer des messages de remerciement aux contributeurs
- **Temps réel** : Mises à jour en temps réel via WebSocket

## Installation

1. Clonez le dépôt :
   ```
   git clone https://github.com/karima-bakbir/Projet_solideshare.git
   cd Projet_solideshare
   ```

2. Créez un environnement virtuel :
   ```
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

4. Initialisez la base de données :
   ```
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. Lancez l'application :
   ```
   python solidshare/app.py
   ```

L'application sera accessible sur http://localhost:5000

## Déploiement

Pour déployer l'application en production, vous pouvez utiliser des services comme Heroku, Railway, Render ou tout autre fournisseur de cloud supportant Python/Flask.

### Exemple de déploiement sur Railway :

1. Créez un compte sur [Railway](https://railway.app)
2. Connectez votre dépôt GitHub
3. Railway détectera automatiquement l'application Flask
4. Configurez les variables d'environnement si nécessaire

## Technologies utilisées

- **Backend** : Flask, SQLAlchemy, Flask-SocketIO
- **Frontend** : HTML, CSS, Bootstrap (via templates Jinja2)
- **Base de données** : SQLite (facilement remplaçable par PostgreSQL en production)
- **Authentification** : Flask-Login
- **Formulaires** : Flask-WTF
- **Temps réel** : Socket.IO

## Structure du projet

```
solidshare/
├── app.py                 # Application principale Flask
├── templates/             # Templates HTML
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── create_group.html
│   ├── group_detail.html
│   ├── request_help.html
│   ├── request_detail.html
│   ├── contribute.html
│   └── thank_you.html
└── static/                # Fichiers statiques (CSS, JS, images)
```

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou à soumettre une pull request.

## Licence

Ce projet est sous licence MIT.
