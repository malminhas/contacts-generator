# contacts-generator
Utility script for generating randomized vcards for smartphone contact testing purposes
 
## Installation
Installation into a virtualenv as follows:
```
$ git clone https://github.com/malminhas/contacts-generator vcards
$ cd vcards
$ mkvirtualenv vcards
$ workon vcards
(vcards) $ pip install --upgrade pip
(vcards) $ pip install docopt, requests, vobject, jsonpickle
(vcards) $ pip freeze -l
docopt==0.6.2
jsonpickle==0.9.3
python-dateutil==2.5.0
requests==2.9.1
six==1.10.0
vobject==0.9.2
(vcards) $ python genvcards.py -h
...
```
## Testing
Setup for running pytest tests:
```
(vcards) $ sudo apt-get install python-py
(vcards) $ pip install pytest
(vcards) $ python -m pytest -v -s tests
```
Note these will fail unless you have setup valid local .app_id and .app_key files as per above.
