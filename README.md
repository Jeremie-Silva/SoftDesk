[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
# SoftDesk
---
### Pré-requis
Avoir un OS **Linux** avec **Python 3.12** installé  
<br/>

### Installation
Executer ces commandes dans un terminal **bash**
pour installer installer le projet
```bash
git clone git@github.com:Jeremie-Silva/SoftDesk.git
cd SoftDesk
pipenv install
pipenv shell
```

Vous aurez peut-être besoin de cette commande :
```
export PIPENV_PYTHON=/usr/bin/python3.12
```

<br/>

lancer l'application en local :
```bash
pipenv run SoftDesk/manage.py runserver
google-chrome http://127.0.0.1:8000/api/ui
```
lancer les tests en local :
```bash
pipenv run SoftDesk/manage.py test soft_desk_api
```