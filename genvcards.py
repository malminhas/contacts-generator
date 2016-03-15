#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# genvcards.py
# (c) 2016 Mal Minhas, <mal@malm.co.uk>
# 
# Notes:
# -----
# * vobject available here: 
#   https://github.com/eventable/vobject
# For documentation see this: http://eventable.github.io/vobject/
# * Mark D found this link for ref on how to pull deleted records from sqlite db:
#   https://github.com/mdegrazia/SQLite-Deleted-Records-Parser/releases
# * Rob C found an alternative tool here:
#   http://www.adamwadeharris.com/heres-how-i-created-20000-fake-contacts-on-the-iphone/
# that uses the coffee script here:
#   https://github.com/andrewppace/vcard-json/blob/master/src/Vcard.coffee
#
# TODO:
# ----
# * generateFakeContact address handling
# * Add more random variation options including language
# 

import os
import time
import json
import requests
import vobject
import jsonpickle

# Fields
SURNAME     = 'Surname'
FORENAME    = 'Forename'
FULLNAME    = 'FullName'
ADDITIONAL  = 'Additional'
PREFIX      = 'Prefix'
SUFFIX      = 'Suffix'
NICKNAME    = 'Nickname'
ROLE        = 'Role'
ORG         = 'Org'
URL         = 'Url'
EMAIL       = 'Email'
TEL         = 'Tel'
ADDR        = 'Address'
BDAY        = 'Birthday'
NOTE        = 'Note'
STREET      = 'Street'
CITY        = 'City'
STATE       = 'State'
POSTCODE    = 'Zip'
COUNTRY     = 'Country'
POBOX       = 'POBox'
PHOTO       = 'Photo'
EXTADR      = 'Extension'

# Modifiers
MAIN        = 'Main'
HOME        = 'Home'
WORK        = 'Work'
MOBILE      = 'Cell'
OTHER       = 'Other'

DEFAULT_NUM_CARDS   =  20  # Default number of cards per account
DEFAULT_NUM_BATCHES =  5   # Default number of batches of output
MAX_BATCHES         = 100
DEFAULT_JPEG_FILE   = 'mickey.jpg'


PROGRAM     = __file__
VERSION     = "1.5"
DATE        = "01-03-16"

def readFromFile(fname):
    with open(fname,'r') as fH:
        return fH.read()


try:
    APP_ID      = readFromFile('.app_id')
    APP_KEY     = readFromFile('.app_key')
except:
    print("Warning: Failed to find and read .app_id or .app_key files")
    APP_ID = None
    APP_KEY = None
    
CONTACT_DB  = 'contacts.json'


class GenvcardsException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class AppIdNotFoundException(GenvcardsException):
    def __init__(self, value):
        super(AppIdNotFoundException,self).__init__(value)

class AppKeyNotFoundException(GenvcardsException):
    def __init__(self, value):
        super(AppKeyNotFoundException,self).__init__(value)


def getFullName(forename, surname, count, index):
    # Make name unique
    n = getForename(forename, count, index) + ' ' + getSurname(surname, count, index)
    return n


def getSurname(surname, count,index):
    s = surname + str(count)
    if index%2 == 0:
        s += str(index)
    return s


def getForename(forename, count,index):
    if forename:
        f = forename + str(count)
    else:
        f = str(count)
    if count%3 == 0:
        f = "M"
    elif index%2 == 0:
        f += str(index)
    return f

        
def changeLastDigits(number,newNumber):
    l=len(str(newNumber))
    return number[0:len(number)-l]+str(newNumber)

        
def getTel(number, count,index):
    # Make each telephone number unique
    n = changeLastDigits(number,count)
    # decide whether to include a number or not always the same for even count
    if count%2 == 0:
        return n
    if index == 3:
        return ''
    if index == 4 or index == 5:
        return changeLastDigits(n,index)
    return n


def getEmail():
    # Make each email unique
    # Add based on index
    return '?'


def getStreet(street,count, index):
    # Make each address unique
    s = street + str(count)
    #vary based on index
    if index%2 == 0:
        return ''
    return s


def getNote(d,vcardfile):
    #offset = vcardfile.find('Vcards')
    #return "This note is for a contact going into %s file for aggregation to %s account" % (vcardfile,vcardfile[:offset])
    return "This note is for a contact going into %s file for aggregation to %s account" % (vcardfile,vcardfile)


def getPhoto(jpegfile):
    # So this was fun. Worked out from: http://stackoverflow.com/questions/25502790/python-django-vcard-photo
    # from which:
    # "You don't need to use base64.encodestring on data because the vobject code does this for you upon setting 
    # encoding_param = 'b'. This wasn't obvious until I looked at the source to discover what was happening."
    #import base64
    with open(jpegfile, 'rb') as image:
        #s = base64.b64encode(image.read())
        s=image.read()
    return s    


def vcardToJson(vcard):
    ''' We assume block encapsulates a single valid vcard that can be parsed by vobject. '''
    d={}
    pvcf = vobject.readOne(vcard)
    attrvals = pvcf.contents
    for k,v in attrvals.iteritems():
        if k in ['email','tel','url','addr']:
            vals = []
            for val in v:
                vals.append(val.value)
                #if val.modifiers: print(k+';'+val.modifiers,val.value)
            d[k] = vals
        elif k in ['org']:
            for val in v:
                d[k] = val.value[0]
        elif k in ['photo']:
            for val in v:
                d[k] = "%d bytes of photo" % len(v[0].value)
        elif k in ['adr']:
            # Value is a vobject.vcard.Address
            adr = v[0].value
            adrarr = []
            if len(adr.street):
                adrarr.append(adr.street)
            if len(adr.city):
                adrarr.append(adr.city)
            if len(adr.region):
                adrarr.append(adr.region)
            if len(adr.code):
                adrarr.append(adr.code)
            if len(adr.country):
                adrarr.append(adr.country)
            if len(adr.box):
                adrarr.append(adr.box)
            if len(adr.extended):
                adrarr.append(adr.extended)
            d[k] = adrarr            
        elif k in ['n']:
            # Value is a vobject.vcard.Name
            name = v[0].value
            namearr = []
            if len(name.family):
                namearr.append(name.family)
            if len(name.given):
                namearr.append(name.given)
            if len(name.additional):
                namearr.append(name.additional)
            if len(name.prefix):
                namearr.append(name.prefix)
            if len(name.suffix):
                namearr.append(name.suffix)
            d[k] = namearr
        else:
            for val in v:
                d[k] = val.value
    # d now filled with goodies.  Let's check it parses ok as valid json:
    json.dumps(d)
    return d


def prettyprintJson(contact):
    # Check that the input is valid JSON
    assert(json.dumps(contact))
    return json.dumps(contact,sort_keys=True,indent=4, separators=(',', ': '))


def procVcardFile(file):
    vcards = []
    with open(file,'r') as f:
        vcfData = f.read()
        if vcfData.find('END:VCARD') > 0:
            vcards=[card+'END:VCARD\n' for card in vcfData.split('END:VCARD')[:-1]]
        else:
            print("FORMAT ERROR: failed to parse valid vcard vcf!")
            print(vcfData)
    return vcards


def generateVcard(d,vcardfile,jpegfile,count,index,pprint=True):
    '''  We construct vobject using dict which represents pull from sqlite db. '''
    vcard = vobject.vCard()
    o = vcard.add('n')
    o.value = vobject.vcard.Name(
                        family=d.get(SURNAME) or '',
                        given=getForename(d.get(FORENAME),count,index),
                        additional=d.get(ADDITIONAL) or '',
                        prefix=d.get(PREFIX) or '',
                        suffix=d.get(SUFFIX) or ''
    )
    o = vcard.add('fn')
    o.value = getFullName(d.get(SURNAME) or '', d.get(FORENAME) or '',count,index)
    if d.get(ORG):
        for v in d.get(ORG):
            o = vcard.add('org')
            o.value = [v]
    for field,typ in [(NICKNAME,'nickname'),(ROLE,'role'),(BDAY,'bday')]:
        if d.get(field):
            o = vcard.add(typ)
            o.value = d.get(field)
    for fieldname,typ in [(EMAIL,'email'),(TEL,'tel'),(URL,'url')]:
        if d.get(fieldname):
            for k,v in d.get(fieldname).items():
                o = vcard.add(typ)
                o.value = v
                #o.modifier
                o.type_param = k
    if d.get(ADDR):
        for k,v in d.get(ADDR).items():
            a = vcard.add('adr')
            a.type_param = k
            a.value = vobject.vcard.Address(
                getStreet(v.get(STREET),count,index),
                city=v.get(CITY) or '',
                region=v.get(STATE) or '',
                code=v.get(POSTCODE) or '',
                country=v.get(COUNTRY) or '',
                box=v.get(POBOX) or '',
                extended=v.get(EXTADR) or ''
            )
    if d.get(NOTE):
        o=vcard.add('note')
        o.value = getNote(d,vcardfile)
    if d.get(PHOTO):
        o=vcard.add('photo')
        o.value = getPhoto(jpegfile)
        o.encoding_param = 'b'
        o.type_param = 'jpeg'
    # Enable this to prettyprint the vobject representation
    # We'd probably prefer to be in JSON here.
    if pprint:
        vcard.prettyPrint()
    # Check to see we can parse the result back to vobject
    s = vcard.serialize()
    pvcard = vobject.readOne(s)
    if d.get(SURNAME):
        assert(pvcard.n.value.family == d.get(SURNAME))
    return s


def generateFakeContact(**kwargs):
    # fakenameapi.com.  Example request:
    # https://v5.fakenameapi.com/generate?
    #       app_id=<app_id>&
    #       app_key=<app_key>&
    #       country=gb&
    #       name-set=en&
    #       gender=random&
    #       minimum-age=19&
    #       maximum-age=85&
    #       output=json&
    #       human=true
    params=["app_id=%s" % APP_ID,"app_key=%s" % APP_KEY,"output=json"]
    for k,v in kwargs.iteritems():
        k = k.replace('_','-')
        params.append("%s=%s" % (k,v))
    if not os.path.exists('.app_id'):
        raise AppIdNotFoundException(".app_id file not present")
    if not os.path.exists('.app_key'):
        raise AppKeyNotFoundException(".app_key file not present")
    url="https://v5.fakenameapi.com/generate?%s" % '&'.join(params)
    print(url)
    try:
        d = requests.get(url,verify=False).json()
        contact = translateFakeFields(d)
        # Add missing fields and adjust others to fit properly with expectations
        contact[TEL] = {HOME:contact.get(TEL)}
        contact[URL] = {WORK:contact.get(URL)}
        contact[EMAIL] = {HOME:contact.get(EMAIL)}
        contact[ORG] = [contact.get(ORG)]
        contact[BDAY] = '-'.join(contact.get(BDAY).split('/')[::-1])
        contact[NICKNAME] = contact.get(FORENAME).lower() + contact.get(SURNAME).lower()[:1]
        
        # TODO: Need to sort out address here...
        
        if contact.get(ADDITIONAL):
            fullname = contact.get(FORENAME) + ' ' + contact.get(ADDITIONAL) + ' ' + contact.get(SURNAME)
        else:
            fullname = contact.get(FORENAME) + ' ' + contact.get(SURNAME)
        contact[FULLNAME] = fullname
    except Exception as e:
        print("Failed to make call on fakenameapi.com: '%s'\nUsing built-in fake contact instead" % e)
        fullname,contact = getExampleFakeContact()
    return fullname, contact


def translateFakeFields(d):
    contact = {}
    tr = {'GivenName':FORENAME,'Surname':SURNAME,'MiddleInitial':ADDITIONAL,'Title':PREFIX,'Birthday':BDAY,
          'Company':ORG,'Occupation':ROLE,'EmailAddress':EMAIL,'Domain':URL,'TelephoneNumber':TEL,
          'StreetAddress':STREET,'City':CITY,'StateFull':STATE,'ZipCode':POSTCODE,'CountryFull':COUNTRY}
    for k,v in d.items():
        tkey = tr.get(k)
        if tkey and len(d.get(k)) > 0:
            contact[tkey] = d.pop(k)
    return contact


def getExampleFakeContact():
    d = {
        PREFIX: u'Ms.',FORENAME: u'Anna',SURNAME: u'Palmer',ADDITIONAL: u'O.', 
        ORG: [u'Allied Radio'],ROLE: u'Web publications designer', BDAY: u'5/2/1940',
        TEL: {HOME:u'079 0163 0342'},EMAIL:{WORK:u'AnnaPalmer@fleckens.hu'},URL: {WORK:u'FeeCourses.co.uk'},
        ADDR:{HOME: {STREET:u'71 Pendwyallt Road',CITY:u'BURTON GREEN',POSTCODE:u'LL12 4AP',COUNTRY:u'United Kingdom'}}
        }
    d[BDAY] = '-'.join(d.get(BDAY).split('/')[::-1])
    fullname = d.get(FORENAME) + ' ' + d.get(ADDITIONAL) + ' ' + d.get(SURNAME)
    d[FULLNAME] = fullname
    d[NICKNAME] = d.get(FORENAME).lower() + d.get(SURNAME).lower()[:1]
    return fullname,d


def generateFakeContacts(N,forceGenerate):
    fakes = readFakeContactDb()
    L = len(fakes)
    generated = []
    print("Length of current contact db=%d" % L)
    for i in range(1,N+1):
        if forceGenerate or not L:
            #print("Generating contact %d" % i)
            fullname,contact = generateFakeContact(country='gb',name_set='en',gender='random',minimum_age=19,maximum_age=85,human='true')
            #print("Created fake contact %d ('%s')" % (i,fullname))
            generated.append((fullname,contact))
            fakes.append((fullname,contact))
        else:
            #print("Retrieving contact %d from database of len %d" % (i,L))
            fullname,contact = getFakeContact(i,fakes)
            #print("Retrieved fake contact %d ('%s')" % (i,fullname))
            generated.append((fullname,contact))
    writeFakeContactDb(fakes)
    return generated


def getFakeContact(i,fakes):
    ''' Returns (fullname,contact) tuple '''
    #print("getFakeContact(%d,%s)" % (i,fakes))
    L = len(fakes)
    assert(L)
    assert(i>=0)
    # Modulo the contact
    name,contact = fakes[i%L]
    return name,contact


def deleteFakeContactDb(db=CONTACT_DB):
    if os.path.exists(db):
        os.remove(db)


def readFakeContactDb(db=CONTACT_DB):
    fakes = []
    try:
        with open(db,'r') as fH:
            frozen = fH.read()
            fakes = jsonpickle.decode(frozen)
    except:
        writeFakeContactDb(fakes,db)
    return fakes


def writeFakeContactDb(fakes,db=CONTACT_DB):
    with open(db,'w') as fH:
        frozen = jsonpickle.encode(fakes)
        fH.write(frozen)


if __name__ == '__main__':
    import docopt
    from docopt import docopt

    usage="""
    
    %s: vCard generation utility
    --------------------------------------
    Can be used to: 
    a) locally store json fake contacts from fakeapiname.com, 
    b) generate output vcard files from stored fake contacts, 
    c) parse vcard files and dump to output as json.
    
    Usage:
      %s generate <ncards> -b <nbatches> [-p <jpeg> <-v]
      %s parse <vcard> [-v]
      %s getfakes <ncards> [-f -v]
      %s -h | --help
      %s -V | --version

    Options:
      -h --help                 Show this screen.
      -v --verbose              Verbose mode.
      -f --force                Force generate fakes.
      -b --nbatches             No. of output batch files.
      -p --jpeg                 Source file for images
      -V --version              Show version.

    Examples:
      %s generate 20 -b 5  # Create 20 vcards in 5 .vcf files
                                     # Uses current contents of local contact store
      %s parse 1.vcf       # Parse vcard '1.vcf' and dump json
      %s getfakes 5        # Cycle through current local contacts store mod 5
      %s getfakes 2 -f     # Force create two new fake contacts 
                                     # New fakes are added to local contacts store
    """ % tuple([PROGRAM] * 10)

    arguments=docopt(usage)
    if arguments.get('--verbose') or arguments.get('-v'):
        VERBOSE = True    
    if arguments.get('--version') or arguments.get('-V'):
        print("%s version %s" % (PROGRAM,VERSION))
    elif arguments.get('--help') or arguments.get('-h'):
       print(usage)
    elif arguments.get('parse'):
        vcardsfile = arguments.get('<vcard>')
        # Get list of all vcards found in vcffile
        vcards = procVcardFile(vcardsfile)
        for i,vcard in enumerate(vcards):
            # Convert each vcard to json
            contact = vcardToJson(vcard)
            print("----- VCARD %d -----\n%s----- JSON ------\n%s" % (i,vcard,prettyprintJson(contact)))
    elif arguments.get('generate'):
        ncards = int(arguments.get('<ncards>')) or DEFAULT_NUM_CARDS
        nbatches = int(arguments.get('<nbatches>')) or DEFAULT_NUM_BATCHES
        if nbatches > MAX_BATCHES:
            print("That's a silly number of batches you're trying to create.  Go away")
            sys.exit()
        jpegfile = arguments.get('<jpeg>') or DEFAULT_JPEG_FILE
        t0 = time.time()
        for i in range(MAX_BATCHES):
            if os.path.exists('Vcards_%d.vcf' % i):
                os.remove('Vcards_%d.vcf' % i)
        vcardFiles = ['Vcards_%d.vcf' % i for i in range(nbatches)]
        fakes = readFakeContactDb()
        for vcardfile in vcardFiles:
            with open(vcardfile,'w') as f:
                for i in range(ncards):
                    fullname,contact = getFakeContact(i,fakes)
                    s = generateVcard(contact,vcardfile,jpegfile,i,vcardFiles.index(vcardfile))
                    print(s)
                    f.write(s)
                    f.write('\n\n')
        t1 = time.time()
        print("----------------------------------------------------------------")
        print("Successfully generated %d vcards each in %d batches in %d seconds" % (ncards,len(vcardFiles),t1-t0))
        print("Generated files: %s" % vcardFiles)
        print("----------------------------------------------------------------")
    elif arguments.get('getfakes'):
        ncards = int(arguments.get('<ncards>')) or DEFAULT_NUM_CARDS
        force = arguments.get('--force') or False
        print("Generate %d fake contacts" % ncards)
        generated = generateFakeContacts(ncards,force)
        for fullname,contact in generated:
            print("----------------------------------------------------------------")
            print("Created '%s':\n%s" % (fullname,prettyprintJson(contact)))
            print("----------------------------------------------------------------")
