import urllib2
import logging
from xml.etree import ElementTree

logging.basicConfig(level=logging.DEBUG)

MS_EXCHANGE_USERNAME = 'vitaliy@daqri.com'
MS_EXCHANGE_PASSWORD = 'xxx'
MS_EXCHANGE_ALL_USERS_FOLDER_ID = 'xxx-xx-4d4a-ace3-e35422131a9f'
MS_EXCHANGE_URL = 'https://outlook.office365.com/ews/Exchange.asmx'

SOAP = """<?xml version="1.0" encoding="UTF-8"?>
    <soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:t="http://schemas.microsoft.com/exchange/services/2006/types" xmlns:m="http://schemas.microsoft.com/exchange/services/2006/messages">
        <soap:Header>
            <t:RequestServerVersion Version="Exchange2013" />
        </soap:Header>
        <soap:Body>
            <m:FindPeople>
                <m:IndexedPageItemView BasePoint="Beginning" MaxEntriesReturned="1000" Offset="0"/>
                <m:ParentFolderId>
                    <AddressListId Id="%s" xmlns="http://schemas.microsoft.com/exchange/services/2006/types" />
                </m:ParentFolderId>
            </m:FindPeople>
        </soap:Body>
    </soap:Envelope>
""" % MS_EXCHANGE_ALL_USERS_FOLDER_ID


auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='', uri=MS_EXCHANGE_URL, user=MS_EXCHANGE_USERNAME, passwd=MS_EXCHANGE_PASSWORD)
opener = urllib2.build_opener(auth_handler, urllib2.HTTPHandler(debuglevel=3))
urllib2.install_opener(opener)


req = urllib2.Request(url=MS_EXCHANGE_URL, data=SOAP)
req.add_header('Content-Type', 'text/xml; charset=utf-8')
response = urllib2.urlopen(req)

root = ElementTree.fromstring(response.read())

persons = []

namespaces = {'env': 'http://schemas.xmlsoap.org/soap/envelope/',
              'msg': 'http://schemas.microsoft.com/exchange/services/2006/messages'}

for person in root.find('env:Body/msg:FindPeopleResponse/msg:People', namespaces=namespaces):
    person_data = {
        'first_name': '',
        'last_name': '',
        'email': '',
        'company': '',
        'im': '',
        'created_at': '',
    }

    for param in person:

        if 'EmailAddresses' in param.tag:
            for email in param[0]:
                if 'EmailAddress' in email.tag:
                    person_data['email'] = email.text

        elif 'GivenName' in param.tag:
            person_data['first_name'] = param.text

        elif 'Surname' in param.tag:
            person_data['last_name'] = param.text

        elif 'Company' in param.tag:
            person_data['company'] = param.text

        elif 'ImAddress' in param.tag:
            person_data['im'] = param.text

        elif 'CreationTime' in param.tag:
            person_data['created_at'] = param.text

    persons.append(person_data)


for i, p in enumerate(persons):
    print str(i).ljust(3), p['first_name'].ljust(15), p['last_name'].ljust(15), p['email'].ljust(35), \
        p['im'].ljust(45), p['company'].ljust(20), p['created_at'].ljust(20)

# TODO: use persons array
