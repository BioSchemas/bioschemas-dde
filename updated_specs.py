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

def add_conformsTo(spec_list,x):
    spec_info = spec_list.loc[spec_list['name']==x['@id'].replace("bioschemas:","")]
    spec_url = spec_info.iloc[0]['url']
    conformsTodict = {
            "description": "This is used to state the Bioschemas profile that the markup relates to. The identifier can be the url for the version of this bioschemas class on github: "+spec_url,
            "$ref": "#/definitions/conformsDefinition"
          }
    conformdef={
                "@type": "CreativeWork",
                "type": "object",
                "properties": {
                  "identifier":{
                    "description": "The url of the version bioschemas profile that was used. For jsonschema, set @id to the identifier",
                    "oneOf": [
                      {
                        "enum": [spec_url] 
                      },
                      {
                        "type": "string",
                        "format": "uri"
                      }
                    ]
                  }
                },
                "required": [
                  "identifier"
                ]              
        }
    x['$validation']['properties']['conformsTo'] = conformsTodict
    requirementlist = x['$validation']['required']
    requirementlist.append('conformsTo')
    x['$validation']['required'] = requirementlist
    try:
        definitiondict = x['$validation']['definitions']
    except:
        definitiondict = {}
    definitiondict["conformsDefinition"]=conformdef
    x['$validation']['definitions']=definitiondict
    return(x)

def add_schemaVersion(spec_list,x):
    spec_info = spec_list.loc[spec_list['name']==x['@id'].replace("bioschemas:","")]
    spec_url = spec_info.iloc[0]['url']
    baseurl = "https://bioschemas.org"
    versionurl = baseurl+'/'+spec_info.iloc[0]['type'].lower()+'s/'+spec_info.iloc[0]['name']+'/'+spec_info.iloc[0]['version']
    try:
        existingversions = x["schema:schemaVersion"]
        if isinstance(schemaversions, list) == False:
            schemaversions = existingversions.strip("[").strip("]").split(",")
        else:
            schemaversions = existingversions
    except:
        schemaversions = []
    schemaversions.append(versionurl)
    schemaversions.append(spec_url)
    ## Ensure uniqueness of elements
    x["schema:schemaVersion"] = list(set(schemaversions))
    return(x)

def clean_duplicate_classes(spec_list,graphlist,classlist):
    duplicates = [i for i in set(classlist) if classlist.count(i) > 1]
    nondupes = [x for x in classlist if x not in duplicates]
    cleanclassgraph = []
    if len(duplicates)>0:  ## There are duplicate classes to clean up
        for x in graphlist:
            if x["@id"] in nondupes:
                y = add_conformsTo(spec_list,x)
                z = add_schemaVersion(spec_list,y)
                cleanclassgraph.append(z)
            for eachclass in duplicates:
                if x["@id"]==eachclass:
                    if "$validation" in x.keys():
                        y = add_conformsTo(spec_list,x)
                        z = add_schemaVersion(spec_list,y)
                        cleanclassgraph.append(z)
    else:  ## There are not duplicate classes to clean up
        for x in graphlist:
            if x["@id"] in nondupes:
                y = add_conformsTo(spec_list,x)
                z = add_schemaVersion(spec_list,y)
                cleanclassgraph.append(z)        
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
    cleanclassgraph = clean_duplicate_classes(spec_list,graphlist,classlist)
    cleanpropsgraph = clean_duplicate_properties(graphlist, propertylist)
    cleangraph = []
    for z in cleanclassgraph:
        cleangraph.append(z)
    for a in cleanpropsgraph:
        cleangraph.append(a)
    conformsTo = define_conformsTo(classlist)
    cleangraph.append(conformsTo)
    bioschemas_json['@graph']=cleangraph
    return(bioschemas_json)

def define_conformsTo(classlist):
    uniqueclasses =  list(set(classlist))
    classidlist = [{"@id":x} for x in classlist]
    conformsTo = {
      "@id": "dct:conformsTo",
      "@type": "rdf:Property",
      "rdfs:comment": "Used to state the Bioschemas profile that the markup relates to. The versioned URL of the profile must be used. Note that we use a CURIE in the table here but the full URL for Dublin Core terms must be used in the markup (http://purl.org/dc/terms/conformsTo), see example.",
      "rdfs:label": "conformsTo",
      "schema:domainIncludes": classidlist,
      "schema:rangeIncludes": [
        {"@id": "schema:CreativeWork"},{"@id": "schema:Text"},{"@id": "schema:Thing"}
      ]
    }
    return(conformsTo)

def update_specs(script_path):
    spec_list = read_csv('specifications_list.txt',delimiter='\t',header=0)
    bioschemas_json = merge_specs(spec_list)
    bioschemasfile = os.path.join(script_path,'bioschemas.json')
    with open(bioschemasfile,'w') as outfile:
        outfile.write(json.dumps(bioschemas_json))

#### Main
script_path = pathlib.Path(__file__).parent.absolute()
update_specs(script_path)