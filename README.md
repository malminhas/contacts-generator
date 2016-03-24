# contacts-generator
Utility script for generating randomized vcards for smartphone contact testing purposes

## Description
```contacts-generator``` can be used to create and locally store fake contacts retrieved 
from fakeapiname.com web service in JSON format.  These contacts can be used to generate 
an arbitrary number of vcards for contacts sync test purposes for example.  Finally, a 
the script allows vcards to to be parsed and converted into the supported JSON format.

IMPORTANT: In order to use this script, you will need to register with the [fakeapiname](https://www.fakenameapi.com/)
service and store your valid ```app_id``` and ```app_key``` credentials in corresponding files 
named ```.app_id``` and ```.app_key``` stored in the same directory as this script.
It is possible to register with [fakeapiname](https://www.fakenameapi.com/) for free. 
There is a rate cap on the number of new contacts you can generate in a day.
Depending on interest, a future version may allow random contact generation without 
access to this API.

Command-line as follows:
```

    genvcards.py: vCard generation utility
    --------------------------------------
    Can be used to:
    a) locally store json fake contacts from fakeapiname.com,
    b) generate output vcard files from stored fake contacts,
    c) parse vcard files and dump to output as json.

    Usage:
      genvcards.py generate <ncards> -b <nbatches> [-p <jpeg> <-v]
      genvcards.py parse <vcard> [-v]
      genvcards.py getfakes <ncards> [-f -v]
      genvcards.py -h | --help
      genvcards.py -V | --version

    Options:
      -h --help                 Show this screen.
      -v --verbose              Verbose mode.
      -f --force                Force generate fakes.
      -b --nbatches             No. of output batch files.
      -p --jpeg                 Source file for images
      -V --version              Show version.

    Examples:
      genvcards.py generate 20 -b 5  # Create 20 vcards in 5 .vcf files
                                     # Uses current contents of local contact store
      genvcards.py parse 1.vcf       # Parse vcard '1.vcf' and dump json
      genvcards.py getfakes 5        # Cycle through current local contacts store mod 5
      genvcards.py getfakes 2 -f     # Force create two new fake contacts
                                     # New fakes are added to local contacts store
```
 
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
