import json
import requests
from pandas import read_csv

def get_raw_url(url):
    if 'raw' not in url:
        rawrawurl = url.replace('github.com','raw.githubusercontent.com')
        rawurl = rawrawurl.replace('/blob/master/','/master/')
    else:
        rawurl = url
    return(rawurl)

def rename_namespace(spec_list,eachurl,rawtext):
    tmpinfo = spec_list.loc[spec_list['url']==eachurl]
    tmpnamespace = tmpinfo.iloc[0]['namespace']
    if namespace!='bioschemas'
        tmptext = '"@id": "'+tmpnamespace+':'
        cleantext = rawtext.replace(tmptext,'"@id": "bioschemas:')
    else:
        cleantext = rawtext
    return(cleantext)

def merge_specs(spec_list):
    bioschemas_json = {}
    graphlist = []
    for eachurl in spec_list['url']:
        rawurl = get_raw_url(eachurl)
        r = requests.get(rawurl)
        if r.status_code == 200:
            cleantext = rename_namespace(spec_list,eachurl,r.text)
            spec_json = json.loads(cleantext)
            bioschemas_json['@context'] = spec_json['@context']
            for x in spec_json['@graph']:
                if x not in graphlist:
                    graphlist.append(x)
    bioschemas_json['@graph']=graphlist
    return(bioschemas_json)

def update_specs():
    spec_list = read_csv('specifications_list.txt',delimiter='\t',header=0)
    bioschemas_json = merge_specs(spec_list)
    with open('bioschemas.json','wb') as outfile:
        json.dump(bioschemas_json,outfile)

#### Main
update_specs()