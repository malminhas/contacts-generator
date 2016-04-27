import pytest
import sys, os

currpath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, currpath + '/../')

# Notes:
# -------
# To run this test from root directory lying:
# $ py.test -v -s
#

import pytest
import genvcards as gv

# -------------------- FIXTURES -------------------

# 1. Contacts 
''' Enable this to mock the call
d = {u'TelephoneNumber': u'079 3953 6764', u'City': u'SPELLBROOK', u'Title': u'Mrs.', u'TropicalZodiac': u'Libra', u'MiddleInitial': u'C', u'Number': 1, u'Latitude': 51.769207, 
u'State':u'', u'WesternUnionMTCN': u'7756494521', u'Vehicle': u'2008 Buick Park Avenue', 
u'BrowserUserAgent': u'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.109 Safari/537.36', 
u'Centimeters': 151, u'GivenName': u'Caitlin', u'Username': u'Whensinal', u'BloodType': u'A-', u'GUID': u'c37b37ba-7647-4fe0-95f2-9522665fc01e', 
u'MoneyGramMTCN': u'61216018', u'Kilograms': u'56.0', u'Company': u'Strawberries', u'CCExpires': u'8/2017', u'CCType': u'MasterCard', u'StateFull': 
u'', u'Birthday': u'10/1/1932', u'Country': u'GB', u'Password': u'uethof9Ee', u'CCNumber': u'5406824962256154', u'NationalID': u'XT 31 52 97 C', 
u'TelephoneCountryCode': 44, u'Pounds': u'123.2', u'Gender': u'female', u'Age': None, u'Longitude': 0.141445, u'StreetAddress': u'67 Hampton Court Rd', 
u'CVV2': u'526', u'CountryFull': u'United Kingdom', u'MothersMaiden': u'Rowley', u'UPS': u'1Z 160 09Y 08 3188 2754', 
u'NameSet': u'England/Wales', u'Domain': u'LoungeTown.co.uk', u'Surname': u'Sanders', u'Color': u'Green', u'ZipCode': u'CM23 9UD', 
u'EmailAddress': u'CaitlinSanders@superrito.com'
, u'FeetInches': u'4\' 11"', u'Occupation': u'Staffing manager'}
'''

# 2. Contact DB
    
# -------------------- TESTS -------------------

TESTDB = 'testdb.json'

def emptyContactDb():
    gv.deleteFakeContactDb(TESTDB)
    assert (not os.path.exists(TESTDB))
    fakes = gv.readFakeContactDb(TESTDB)
    assert(isinstance(fakes, list))
    assert(len(fakes) == 0)

def addToContactDb(N):
    contact = gv.getExampleFakeContact()
    jsondata = gv.prettyprintJson(contact)
    #print(jsondata)
    contacts = [contact]*N
    gv.writeFakeContactDb(contacts,TESTDB)
    fakes = gv.readFakeContactDb(TESTDB)
    assert(isinstance(fakes, list))
    assert(len(fakes) == N)
    return contacts

class TestFakeContactDb:
    """
    Testing genvcards local fake contact db support
        - readFakeContactDb()
        - writeFakeContactDb()
        - deleteFakeContactDb()
    """
    
    def testFakeContactDb(self):
        print("\n-------------- TestFakeContactDb -----------")
        # 1. Test empty contacts db
        emptyContactDb()
        # 2. Test that adding a single contact works
        contacts = addToContactDb(1)
        contact = contacts[0]
        # 3. Test that adding N in range 0..10 contacts works ok
        N = 30
        for i in range(0,N):
            contacts = [contact] * N
            gv.writeFakeContactDb(contacts,TESTDB)
            assert(os.path.exists(TESTDB))
            fakes = gv.readFakeContactDb(TESTDB)
            assert(isinstance(fakes,list))
            assert(len(fakes) == N)
        # 4. Test empty contacts db
        emptyContactDb()


class TestFakes:
    """
    Testing genvcards fake contact generation:
        - getExampleFakeContact()
        - getFakeContact()
        - generateFakeContacts()
        - generateFakeContact()
    """

    def testFakes(self):
        print("\n-------------- TestFakes -----------")
        emptyContactDb()
        # 1. Test that adding a single fake contact using built-in fake
        contacts = addToContactDb(1)
        fullname0,contact0 = contacts[0]
        if os.path.exists('.app_id') and os.path.exists('.app_key'):
            # 2. Test generateFakeContact() correctly raises exceptions with missing local credential files
            os.rename('.app_id','.app_id.move')
            print(os.path.exists('.app_id.move'))
            # Use pytest.raises for testing exceptions your own code is deliberately raising:
            with pytest.raises(gv.AppIdNotFoundException):
                fullname1,contact1 = gv.generateFakeContact(country='gb', name_set='en', gender='random', minimum_age=19,
                                                        maximum_age=85, human='true',callapi=True)
            os.rename('.app_id.move','.app_id')
            os.rename('.app_key','.app_key.move')
            with pytest.raises(gv.AppKeyNotFoundException):
                fullname1,contact1 = gv.generateFakeContact(country='gb', name_set='en', gender='random', minimum_age=19,
                                                        maximum_age=85, human='true',callapi=True)
            os.rename('.app_key.move','.app_key')
            # 3. Test generateFakeContact() works on happy path - assumes credential files are valid
            fullname1,contact1 = gv.generateFakeContact(country='gb', name_set='en', gender='random', minimum_age=19,
                                                    maximum_age=85, human='true',callapi=True)
            assert(fullname1)
            assert(contact1)
            assert(fullname0 != fullname1)
            fakes = gv.readFakeContactDb(TESTDB)
            fakes.append((fullname1,contact1))
            gv.writeFakeContactDb(fakes,TESTDB)
            assert (isinstance(fakes, list))
            assert (len(fakes) == 2)
            fname, cont = gv.getFakeContact(0, fakes)
            assert (fullname0 == fname)
            assert (contact0 == cont)
            fname, cont = gv.getFakeContact(1, fakes)
            assert (fullname1 == fname)
            assert (contact1 == cont)
        else:
            print('WARNING: .app_id or .app_key not found!')
        emptyContactDb()

class TestGenerate:
    """
    Testing genvcards vcf generation:
        - generateVcard()
    """

    def testGenerate(self):
        print("\n-------------- TestGenerate -----------")
        emptyContactDb()
        # 1. Test that adding a single fake contact using built-in fake
        contacts = addToContactDb(1)
        fullname, contact = contacts[0]
        # There has to be at least one in the db for this to work
        jpegfile = gv.DEFAULT_JPEG_FILE
        nbatches = 1
        ncards = 2
        vcardFiles = ['Vcards_%d.vcf' % i for i in range(nbatches)]
        fakes = gv.readFakeContactDb(TESTDB)
        for vcardfile in vcardFiles:
            with open(vcardfile, 'w') as f:
                for i in range(ncards):
                    fullname, contact = gv.getFakeContact(i, fakes)
                    s = gv.generateVcard(contact, vcardfile, jpegfile, i, vcardFiles.index(vcardfile),pprint=False)
                    f.write(s)
        fakes = gv.readFakeContactDb(TESTDB)
        assert (isinstance(fakes, list))
        assert (len(fakes) == 1)
        emptyContactDb()
        

class TestParse:
    """
    Testing genvcards vcf parse support:
        - procVcardFile()
        - vcardToJson()
        - generateVcard()
    """

    def testParse(self):
        print("\n-------------- TestParse -----------")
        vcardfiles = ['Vcards_0.vcf']
        # Get list of all vcards found in vcardfile
        vcardfile = vcardfiles[0]
        vcards = gv.procVcardFile(vcardfile)
        for i,vcard in enumerate(vcards):
            # Convert each vcard to json
            jpegfile = None
            contact = gv.vcardToJson(vcard)
            print('----- CONTACT %d (%s) -----' % (i,contact.get('n')))
            print(gv.prettyprintJson(contact)[:64] + "\n...")
            s = gv.generateVcard(contact, vcardfile, jpegfile, i, vcardfiles.index(vcardfile),pprint=False)
