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
```

```bash
virtualenv -p3.12 .venv
source .venv/bin/activate
pip install --upgrade setuptools
pip install -r requirements.txt
```

<br/>

lancer l'application en local :
```bash
python SoftDesk/manage.py runserver
google-chrome http://127.0.0.1:8000/
```
