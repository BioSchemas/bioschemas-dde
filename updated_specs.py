import json
import requests
import pandas as pd
from pandas import read_csv
import os
import pathlib

def get_raw_url(url):
    if 'raw' not in url:
        rawrawurl = url.replace('github.com','raw.githubusercontent.com')
        if 'master' in rawrawurl:
            rawurl = rawrawurl.replace('/blob/master/','/master/')
        elif 'main' in rawrawurl:
            rawurl = rawrawurl.replace('/blob/main/','/main/')
    else:
        rawurl = url
    return(rawurl)

def rename_namespace(spec_list,eachurl,rawtext):
    tmpinfo = spec_list.loc[spec_list['url']==eachurl]
    tmpnamespace = tmpinfo.iloc[0]['namespace']
    if tmpnamespace!='bioschemas':
        tmptext = '"@id": "'+tmpnamespace+':'
        cleantext = rawtext.replace(tmptext,'"@id": "bioschemas:')
    else:
        cleantext = rawtext
    return(cleantext)

def check_context_url(spec_json):
    contextInfo = spec_json['@context']
    bioschemasUrl = "https://discovery.biothings.io/view/bioschemas/"
    contextInfo["bioschemas"]=bioschemasUrl
    return(contextInfo)

def update_subclass(spec_list,eachurl,cleantext):
    spec_json = json.loads(cleantext)
    tmpinfo = spec_list.loc[spec_list['url']==eachurl]
    tmpsubclass = tmpinfo.iloc[0]['subclassOf']
    classname = tmpinfo.iloc[0]['name']
    truesubclass = {"@id": tmpsubclass}
    for x in spec_json['@graph']:
        if x['@id']=="bioschemas:"+classname:
            x['rdfs:subClassOf']=truesubclass
    return(spec_json)

def clean_duplicate_classes(graphlist,classlist):
    duplicates = [i for i in set(classlist) if classlist.count(i) > 1]
    nondupes = [x for x in classlist if x not in duplicates]
    if len(duplicates)>0:  ## There are duplicate classes to clean up
        cleanclassgraph = []
        for x in graphlist:
            if x["@id"] in nondupes:
                cleanclassgraph.append(x)
            for eachclass in duplicates:
                if x["@id"]==eachclass:
                    if "$validation" in x.keys():
                        cleanclassgraph.append(x)
    return(cleanclassgraph)

def clean_duplicate_properties(graphlist, propertylist):            
    duplicates = [i for i in set(propertylist) if propertylist.count(i) > 1]
    nondupes = [x for x in propertylist if x not in duplicates]
    if len(duplicates)>0:  ## There are duplicate properties to clean up
        cleanpropsgraph = []
        dupepropsgraph = []
        for x in graphlist:
            if x["@id"] in nondupes:
                cleanpropsgraph.append(x)
            elif x["@id"] in duplicates:
                dupepropsgraph.append(x)
        #dupepropsgraph[0]["dummyProp"]={"@id":"dummyValue"} #### creates dummy property for testing only
        dupepropsdf = pd.DataFrame(dupepropsgraph)
        for eachprop in duplicates:
            tmpdf = dupepropsdf.loc[dupepropsdf['@id']==eachprop].copy()
            domainlist = []
            domainlist = [y for y in tmpdf["schema:domainIncludes"] if y not in domainlist]
            #### Get the row with the least number of NaNs (ie- the row with the most properties) to serve as the base property
            tmpdf["nullcount"]=tmpdf.isnull().sum(axis=1)
            tmpdf.sort_values("nullcount",ascending=True,inplace=True)
            tmpdict = tmpdf.iloc[0].to_dict()
            del tmpdict["nullcount"]
            tmpdict["schema:domainIncludes"]=domainlist #### Set the domainIncludes list
            cleanpropsgraph.append(tmpdict)       
    else:
        for x in graphlist:
            if x["@id"] in nondupes:
                cleanpropsgraph.append(x)
    return(cleanpropsgraph)

def merge_specs(spec_list):
    bioschemas_json = {}
    graphlist = []
    classlist = []
    propertylist = []
    for eachurl in spec_list['url']:
        rawurl = get_raw_url(eachurl)
        r = requests.get(rawurl)
        if r.status_code == 200:
            cleantext = rename_namespace(spec_list,eachurl,r.text)
            spec_json = json.loads(cleantext)
            bioschemas_json['@context'] = check_context_url(spec_json)
            for x in spec_json['@graph']:
                graphlist.append(x)
                if x["@type"]=="rdfs:Class":
                    classlist.append(x["@id"])
                if x["@type"]=="rdf:Property":
                    propertylist.append(x["@id"])
    cleanclassgraph = clean_duplicate_classes(graphlist,classlist)
    cleanpropsgraph = clean_duplicate_properties(graphlist, propertylist)
    cleangraph = []
    for z in cleanclassgraph:
        cleangraph.append(z)
    for a in cleanpropsgraph:
        cleangraph.append(a)
    bioschemas_json['@graph']=cleangraph
    return(bioschemas_json)

def update_specs(script_path):
    spec_list = read_csv('specifications_list.txt',delimiter='\t',header=0)
    bioschemas_json = merge_specs(spec_list)
    bioschemasfile = os.path.join(script_path,'bioschemas.json')
    with open(bioschemasfile,'w') as outfile:
        outfile.write(json.dumps(bioschemas_json))

#### Main
script_path = pathlib.Path(__file__).parent.absolute()
update_specs(script_path)