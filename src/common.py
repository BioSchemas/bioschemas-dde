import json
import requests
import pandas as pd
from pandas import read_csv
import os
import pathlib
from datetime import datetime
from datetime import timedelta
from biothings_schema import Schema

def get_raw_url(url):
    if 'raw' not in url:
        rawrawurl = url.replace('github.com','raw.githubusercontent.com')
        if 'master' in rawrawurl:
            rawurl = rawrawurl.replace('/blob/master/','/master/').replace('/tree/master/','/master/')
        elif 'main' in rawrawurl:
            rawurl = rawrawurl.replace('/blob/main/','/main/').replace('/tree/master/','/master/')
    else:
        rawurl = url
    return rawurl

def rename_namespace(spec_list,eachurl,rawtext):
    tmpinfo = spec_list.loc[spec_list['url']==eachurl]
    tmpnamespace = tmpinfo.iloc[0]['namespace']
    if 'DEPRECATED' in tmpinfo.iloc[0]['version']:
        if tmpnamespace!='bioschemasdeprecated':
            tmptext = '"@id": "'+tmpnamespace+':'
            cleantext = rawtext.replace(tmptext,'"@id": "bioschemasdeprecated:')
        else:
            cleantext = rawtext 
    elif ((tmpinfo.iloc[0]['type']=='Profile') and ('RELEASE' in tmpinfo.iloc[0]['version'])):
        if tmpnamespace!='bioschemas':
            tmptext = '"@id": "'+tmpnamespace+':'
            cleantext = rawtext.replace(tmptext,'"@id": "bioschemas:')
        else:
            cleantext = rawtext
    elif ((tmpinfo.iloc[0]['type']=='Profile') and ('DRAFT' in tmpinfo.iloc[0]['version'])):
        if tmpnamespace!='bioschemasdrafts':
            tmptext = '"@id": "'+tmpnamespace+':'
            cleantext = rawtext.replace(tmptext,'"@id": "bioschemasdrafts:')
        else:
            cleantext = rawtext  
    elif ((tmpinfo.iloc[0]['type']=='Type') and ('RELEASE' in tmpinfo.iloc[0]['version'])):
        if tmpnamespace!='bioschemastypes':
            tmptext = '"@id": "'+tmpnamespace+':'
            cleantext = rawtext.replace(tmptext,'"@id": "bioschemastypes:')
        else:
            cleantext = rawtext
    elif ((tmpinfo.iloc[0]['type']=='Type') and ('DRAFT' in tmpinfo.iloc[0]['version'])):
        if tmpnamespace!='bioschemastypesdrafts':
            tmptext = '"@id": "'+tmpnamespace+':'
            cleantext = rawtext.replace(tmptext,'"@id": "bioschemastypesdrafts:')
        else:
            cleantext = rawtext
    return(cleantext, tmpnamespace)

        
def get_context_exclusions(spec_list):
    namespace = spec_list.iloc[0]['namespace']
    if namespace in ['bioschemastypes', 'bioschemastypesdrafts']:
        return {'bioschemas', 'bioschemasdeprecated', 'bioschemasdrafts'}
    return set()


def generate_base_context(excluded_contexts=None):
    if excluded_contexts is None:
        excluded_contexts = set()
    allcontext = {
        "schema": "http://schema.org/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "owl":"http://www.w3.org/2002/07/owl/",
        "bioschemas":"https://discovery.biothings.io/ns/bioschemas/",
        "bioschemasdrafts":"https://discovery.biothings.io/ns/bioschemasdrafts/",
        "bioschemastypes":"https://discovery.biothings.io/ns/bioschemastypes/",
        "bioschemastypesdrafts":"https://discovery.biothings.io/ns/bioschemastypesdrafts/",
        "bioschemasdeprecated":"https://discovery.biothings.io/ns/bioschemasdeprecated/",
        "dct":"http://purl.org/dc/terms/"
    }
    for context_key in excluded_contexts:
        allcontext.pop(context_key, None)
    return allcontext


def check_context_url(allcontext,spec_json,tmpnamespace,excluded_contexts=None):
    if excluded_contexts is None:
        excluded_contexts = set()
    now = datetime.now()
    contextInfo = spec_json['@context']
    for key in list(contextInfo.keys()):
        if key != tmpnamespace and key not in excluded_contexts:
            if key not in list(allcontext.keys()):
                allcontext[key] = contextInfo[key]
    allcontext["@dateModified"] = now.strftime("%m/%d/%Y, %H:%M:%S")
    return allcontext


def build_subclass_value(tmpsubclass):
    subclass_names = [x.strip() for x in str(tmpsubclass).split(',') if x.strip()]
    if len(subclass_names) > 1:
        return [{"@id": subclass_name} for subclass_name in subclass_names]
    if len(subclass_names) == 1:
        return {"@id": subclass_names[0]}
    return None


def get_expected_graph_id(spec_row):
    if 'DEPRECATED' in spec_row['version']:
        namespace = 'bioschemasdeprecated'
    elif spec_row['type'] == 'Profile' and 'RELEASE' in spec_row['version']:
        namespace = 'bioschemas'
    elif spec_row['type'] == 'Profile' and 'DRAFT' in spec_row['version']:
        namespace = 'bioschemasdrafts'
    elif spec_row['type'] == 'Type' and 'RELEASE' in spec_row['version']:
        namespace = 'bioschemastypes'
    elif spec_row['type'] == 'Type' and 'DRAFT' in spec_row['version']:
        namespace = 'bioschemastypesdrafts'
    else:
        namespace = spec_row['namespace']
    return namespace + ':' + spec_row['name']


def normalize_subclass_values(subclass_value):
    if isinstance(subclass_value, list):
        values = []
        for item in subclass_value:
            if isinstance(item, dict):
                if '@id' in item:
                    values.append(item['@id'])
            elif isinstance(item, str):
                values.append(item)
        return sorted(set(values))
    if isinstance(subclass_value, dict):
        if '@id' in subclass_value:
            return [subclass_value['@id']]
        return []
    if subclass_value is None or pd.isna(subclass_value):
        return []
    if isinstance(subclass_value, str):
        return sorted(set([x.strip() for x in subclass_value.split(',') if x.strip()]))
    return []


def verify_subclass_values(spec_list, bioschemas_json):
    class_graph = {
        item['@id']: item for item in bioschemas_json['@graph']
        if item.get('@type') == 'rdfs:Class'
    }
    mismatches = []
    for _, spec_row in spec_list.iterrows():
        expected_id = get_expected_graph_id(spec_row)
        graph_item = class_graph.get(expected_id)
        if graph_item is None:
            mismatches.append({
                'class': expected_id,
                'reason': 'missing class in json graph'
            })
            continue
        table_subclass = normalize_subclass_values(spec_row['subClassOf'])
        json_subclass = normalize_subclass_values(graph_item.get('rdfs:subClassOf'))
        if table_subclass != json_subclass:
            mismatches.append({
                'class': expected_id,
                'table_subClassOf': table_subclass,
                'json_subClassOf': json_subclass
            })
    return mismatches


def update_subclass(spec_list,eachurl,cleantext):
    spec_json = json.loads(cleantext)
    tmpinfo = spec_list.loc[spec_list['url']==eachurl]
    tmpsubclass = tmpinfo.iloc[0]['subClassOf']
    classname = tmpinfo.iloc[0]['name']
    truesubclass = build_subclass_value(tmpsubclass)
    if truesubclass is None:
        return spec_json
    for x in spec_json['@graph']:
        if x['@id']=="bioschemas:"+classname:
            x['rdfs:subClassOf']=truesubclass
        if x['@id']=="bioschemasdrafts:"+classname:
            x['rdfs:subClassOf']=truesubclass
        if x['@id']=="bioschemastypes:"+classname:
            x['rdfs:subClassOf']=truesubclass
        if x['@id']=="bioschemastypesdrafts:"+classname:
            x['rdfs:subClassOf']=truesubclass
        if x['@id']=="bioschemasdeprecated:"+classname:
            x['rdfs:subClassOf']=truesubclass
    return spec_json

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


def deletenamespace(x):
    oldname = x['@id']
    if "bioschemastypesdrafts" in oldname:
        cleanname = oldname.replace("bioschemastypesdrafts:","")        
    elif "bioschemastypes" in oldname:
        cleanname = oldname.replace("bioschemastypes:","")
    elif "bioschemasdrafts" in oldname:
        cleanname = oldname.replace("bioschemasdrafts:","")
    elif "bioschemasdeprecated" in oldname:
        cleanname = oldname.replace("bioschemasdeprecated:","")
    elif "bioschemas" in oldname:
        cleanname = oldname.replace("bioschemas:","")
    return cleanname


def remove_conformsTo(x):
    if 'conformsTo' in list(x['$validation']['properties'].keys()):
        del x['$validation']['properties']['conformsTo']
        requirementlist = [i for i in x['$validation']['required'] if i!='conformsTo']
        x['$validation']['required'] = requirementlist
    if 'definitions' in list(x['$validation']):
        if 'conformsTo' in list(x['$validation']['definitions'].keys()):
            del x['$validation']['definitions']['conformsTo']
        if 'conformsDefinition' in list(x['$validation']['definitions'].keys()):
             del x['$validation']['definitions']['conformsDefinition']
    return x


def add_conformsTo(spec_list,x):
    cleanname = deletenamespace(x)
    spec_info = spec_list.loc[spec_list['name'] == cleanname]
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
    return x


def add_schemaVersion(spec_list,x):
    cleanname = deletenamespace(x)
    spec_info = spec_list.loc[spec_list['name'] == cleanname]
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
    return x


def add_specification_type(spec_list,x):
    cleanname = deletenamespace(x)
    spec_info = spec_list.loc[spec_list['name'] == cleanname]
    if spec_list.iloc[0]['type']=='Type':
        baseurl = 'https://bioschemas.org/types#nav-'
    elif spec_list.iloc[0]['type']=='Profile':
        baseurl = 'https://bioschemas.org/profiles#nav-'
    if 'deprecated' in spec_info.iloc[0]['version'].lower():
        typeurl = baseurl+'deprecated'
    elif 'release' in spec_info.iloc[0]['version'].lower():
        typeurl = baseurl+'release'
    elif 'draft' in spec_info.iloc[0]['version'].lower():
        typeurl = baseurl+'draft'
    x['additional_type'] = typeurl
    return x


def remove_NaN_fields(propdef):
    cleandict = {}
    if isinstance(propdef,dict):
        for k, v in propdef.items():
            if k != "schema:sameAs":
                cleandict[k]=v
            elif k == "schema:sameAs": 
                if isinstance(v,type(None))==False:
                    cleandict[k]=v
    if isinstance(propdef,str):
        cleandict = propdef.replace(', "schema:sameAs": NaN','')
        cleandict = cleandict.replace('"schema:sameAs": NaN, ','')
    return cleandict


def sort_graph_objects(graphlist):
    def graph_type_order(item):
        item_type = item.get("@type", "")
        if item_type == "rdfs:Class":
            return 0
        if item_type == "rdf:Property":
            return 1
        return 2

    def graph_name(item):
        item_id = item.get("@id", "")
        if ":" in item_id:
            return item_id.split(":", 1)[1].lower()
        return item_id.lower()

    return sorted(graphlist, key=lambda item: (graph_type_order(item), graph_name(item)))


def clean_duplicate_classes(spec_list,graphlist,classlist):
    duplicates = [i for i in set(classlist) if classlist.count(i) > 1]
    nondupes = [x for x in classlist if x not in duplicates]
    cleanclassgraph = []
    if len(duplicates)>0:  ## There are duplicate classes to clean up
        for x in graphlist:
            if x["@id"] in nondupes:
                x = add_specification_type(spec_list,x)
                x = add_schemaVersion(spec_list,x)
                if "$validation" in x.keys():
                    x = remove_conformsTo(x)
                    x = add_conformsTo(spec_list,x)
                cleanclassgraph.append(x)
            for eachclass in duplicates:
                if x["@id"]==eachclass:
                    x = add_specification_type(spec_list,x)
                    x = add_schemaVersion(spec_list,x)
                    if "$validation" in x.keys():
                        x = remove_conformsTo(x)
                        x = add_conformsTo(spec_list,x)
                    cleanclassgraph.append(x)
    else:  ## There are no duplicate classes to clean up
        for x in graphlist:
            if x["@id"] in nondupes:
                x = add_specification_type(spec_list,x)
                x = add_schemaVersion(spec_list,x)
                if "$validation" in x.keys():
                    x = remove_conformsTo(x)
                    x = add_conformsTo(spec_list,x)
                cleanclassgraph.append(x)        
    return cleanclassgraph


def clean_duplicate_properties(graphlist, propertylist):
    if 'conformsTo' in propertylist:
        propertylist.remove('conformsTo')
    if 'dct:conformsTo' in propertylist:
        propertylist.remove('dct:conformsTo')
    duplicates = [i for i in set(propertylist) if propertylist.count(i) > 1]
    nondupes = [x for x in propertylist if x not in duplicates]
    cleanpropsgraph = []
    dupepropsgraph = []
    if len(duplicates)>0:  ## There are duplicate properties to clean up
        for x in graphlist:
            if x["@id"] in nondupes:
                x = remove_NaN_fields(x)
                cleanpropsgraph.append(x)
            elif x["@id"] in duplicates:
                x = remove_NaN_fields(x)
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
                x = remove_NaN_fields(x)
                cleanpropsgraph.append(x)
    return cleanpropsgraph      


def merge_specs(spec_list):
    bioschemas_json = {}
    graphlist = []
    classlist = []
    propertylist = []
    excluded_contexts = get_context_exclusions(spec_list)
    allcontext = generate_base_context(excluded_contexts)
    for eachurl in spec_list['url']:
        rawurl = get_raw_url(eachurl)
        r = requests.get(rawurl)
        if r.status_code == 200:
            cleantext,tmpnamespace = rename_namespace(spec_list,eachurl,r.text)
            spec_json = update_subclass(spec_list,eachurl,cleantext)
            allcontext = check_context_url(allcontext,spec_json,tmpnamespace,excluded_contexts)
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
    bioschemas_json['@context'] = allcontext
    bioschemas_json['@graph']=sort_graph_objects(cleangraph)
    return bioschemas_json


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
    return conformsTo


def check_for_updates(script_path,updateall=False):
    checktime = datetime.now()
    profile_file = os.path.join(script_path,'profile_list.txt')
    profile_draft_file = os.path.join(script_path,'draft_profile_list.txt')
    type_file = os.path.join(script_path,'type_list.txt')
    type_draft_file = os.path.join(script_path,'draft_type_list.txt')
    deprecated = os.path.join(script_path,'deprecated.txt')
    filelist = [type_file,type_draft_file,profile_file,profile_draft_file,deprecated]
    updatedlist = []
    if updateall==True:
        updatedlist = filelist
    else:
        for eachfile in filelist:
            last_modified = datetime.fromtimestamp(os.path.getmtime(eachfile))
            timediff = checktime-last_modified
            if timediff < timedelta(hours=24):
                updatedlist.append(eachfile)
    if len(updatedlist)==0:
        updatedlist = False
    return updatedlist


def run_update(script_path,updateall=False):
    if updateall == True:
        updatedlist = check_for_updates(script_path,True)
    else:
        updatedlist = check_for_updates(script_path,False)
    print(updateall,updatedlist)
    if updatedlist != False:
        for eachfile in updatedlist:
            speclist = read_csv(eachfile,delimiter='\t',header=0)
            bioschemas_json = remove_NaN_fields(merge_specs(speclist))
            subclass_mismatches = verify_subclass_values(speclist, bioschemas_json)
            if len(subclass_mismatches) > 0:
                raise ValueError(
                    "subClassOf verification failed for "
                    + eachfile
                    + ": "
                    + json.dumps(subclass_mismatches, indent=2)
                )
            jsonstring = json.dumps(bioschemas_json)
            cleanstring = remove_NaN_fields(jsonstring)
            cleandict = json.loads(cleanstring)
            prettystring = json.dumps(cleandict, indent=2)
            #### Check specification list file name to determine where to save
            if "deprecated" in eachfile:
                ####treat as deprecated
                bioschemasfile = os.path.join(script_path,'bioschemasdeprecated.json')
            if "type" in eachfile:
                if "draft" in eachfile:
                    #### draft type treat as type 
                    bioschemasfile = os.path.join(script_path,'bioschemastypesdrafts.json')
                else:
                    ####treat as type
                    bioschemasfile = os.path.join(script_path,'bioschemastypes.json')
            if "profile" in eachfile:
                if "draft" in eachfile:
                    ####treat as draft profile
                    bioschemasfile = os.path.join(script_path,'bioschemasdrafts.json')
                else:
                    bioschemasfile = os.path.join(script_path,'bioschemas.json')
            sc = Schema(cleandict)
            sc.validation
            with open(bioschemasfile,'w') as outfile:
                outfile.write(prettystring)


        
