import os
import json
import pandas as pd
import requests

def convert_to_raw(githuburl): ## Converts a github url to a raw github url
    githubrawurl = githuburl.replace('github.com','raw.githubusercontent.com').replace('blob/','').replace('tree/','')
    return githubrawurl

def load_parent_source():
    parent_source_url = 'https://github.com/BioSchemas/bioschemas.github.io/blob/profile-auto-generation/_data/metadata_mapping.csv'
    parent_source_df = pd.read_csv(convert_to_raw(parent_source_url), header=0,usecols = ['profile','TypeParent','ProfileParent'])
    return parent_source_df

def lookup_parent(parent_source_options,classname,spectype):
    parent_choices = parent_source_options.loc[parent_source_options['profile']==classname]
    if spectype == 'Profile':
        parent = parent_choices.iloc[0]['ProfileParent']
    else:
        parent = parent_choices.iloc[0]['TypeParent']
    return parent

def parse_info_from_json(url,parent_source_options):
    r = requests.get(convert_to_raw(url))
    tmpjson = json.loads(r.text)
    speclass =  [x for x in tmpjson['@graph'] if x["@type"]=="rdfs:Class"]
    speclassid = speclass[0]['@id'].split(':')
    namespace = speclassid[0]
    classname = speclassid[1]
    if '$validation' in list(speclass[0].keys()):
        spectype = 'Profile'
    else:
        spectype = 'Type'
    version = parse_version_from_url(url,classname)
    parent = lookup_parent(parent_source_options,classname,spectype)
    tmpdict = {'namespace':namespace,'name':classname,'subClassOf':parent,'type':spectype,'version':version,'url':url}
    return tmpdict

def generate_base_update_table(script_path):
    updated_specs_folder = os.path.join(script_path,'latest-updated-profiles')
    latest_updates = os.listdir(updated_specs_folder)
    parent_source_options = load_parent_source()
    updated_list = []
    for eachfile in latest_updates:
        filepath = os.path.join(updated_specs_folder,eachfile)
        tmpdf = pd.read_csv(filepath, header=0)
        version = tmpdf.iloc[0]['version']
        url = tmpdf.iloc[0]['url']
        tmpdict = parse_info_from_json(url,parent_source_options)
        updated_list.append(tmpdict)
    updated_df = pd.DataFrame(updated_list)
    return updated_df


def parse_version_from_url(url,classname):
    urlstrlist = url.split('/')
    bioschemasfile = urlstrlist[-1]
    no_ext = bioschemasfile.replace('.JSONLD','').replace('.jsonld','').replace('.JSON','').replace('.json','')
    version = no_ext.replace(classname+'_v','').replace(classname+'_','').replace('-type','').replace('-profile','')
    return version


def check_for_updates(spec_updated_df,original_df):
    update_needed = False
    if len(spec_updated_df)>0:
        update_needed = True
    if update_needed == True:
        original_url_list = original_df['url'].tolist()
        original_alias_list = [x.replace('blob','tree') for x in original_url_list]
        potentially_needs_updates = spec_updated_df.loc[~spec_updated_df['url'].isin(original_url_list)]
        if len(potentially_needs_updates) > 0:
            alias_check = potentially_needs_updates.loc[~potentially_needs_updates['url'].isin(original_alias_list)]
            if len(alias_check) > 0:
                update_needed = True
            else:
                update_needed = False
        else:
            update_needed = False
    return(update_needed)


def compare_versions(a,b):
    greaterlist = ['0.10','0.11','0.12','0.13','0.14','0.15']
    lesserlist = ['0.2','0.3','0.4','0.5','0.6','0.7','0.8','0.9']
    latest_version = None
    if a > b:
        latest_version = a
    else:
        for x in greaterlist:
            if x in a:
                weirdversion = True
                break
            else:
                weirdversion = False
        if weirdversion == False:
            latest_version = b
        else:
            for y in lesserlist:
                if y in b:
                    latest_version = a
                    break
                else:
                    latest_version = b    
    return latest_version


def update_spec_table(eachfile,spec_updated_df):
    original_df = pd.read_csv(os.path.join(script_path,eachfile),delimiter='\t',header=0,
                              usecols=['name','subClassOf','version','url'])
    update_needed = check_for_updates(spec_updated_df,original_df)
    if update_needed == True:
        classes_to_update = spec_updated_df['name'].to_list()
        newdf = original_df.loc[~original_df['name'].isin(classes_to_update)]
        for eachclass in classes_to_update:
            updateversiondf = spec_updated_df.loc[spec_updated_df['name']==eachclass]
            updateversion = updateversiondf.iloc[0]['version']
            oldversiondf = original_df.loc[original_df['name']==eachclass]
            if len(oldversiondf)<=0:
                latestversion = updateversion
            else:
                oldversion = oldversiondf.iloc[0]['version']
                latestversion = compare_versions(updateversion,oldversion)
                if latestversion == updateversion:
                    newdf = pd.concat((newdf,updateversiondf),ignore_index=True)
                else :
                    newdf = pd.concat((newdf,oldversiondf),ignore_index=True)
        newdf.to_csv(os.path.join(script_path,eachfile),sep='\t',header=True,index=False)


def update_tables(script_path):
    updated_df = generate_base_update_table(script_path)
    deprecated = updated_df.loc[updated_df['version'].astype(str).str.contains('DEPRECATED')]
    draftdf = updated_df.loc[updated_df['version'].astype(str).str.contains('DRAFT')]
    releasedf = updated_df.loc[updated_df['version'].astype(str).str.contains('RELEASE')]
    draft_profile = draftdf.loc[draftdf['type']=='Profile']
    draft_type = draftdf.loc[draftdf['type']=='Type']
    released_profile = releasedf.loc[releasedf['type']=='Profile']
    released_type = releasedf.loc[releasedf['type']=='Type']
    filelist = ['deprecated.txt','profile_list.txt','type_list.txt','draft_profile_list.txt','draft_type_list.txt']
    for eachfile in filelist:
        if 'deprecated' in eachfile:
            spec_updated_df = deprecated
            update_spec_table(eachfile,spec_updated_df)
        elif 'profile' in eachfile:
            if 'draft' in eachfile:
                spec_updated_df = draft_profile
                update_spec_table(eachfile,spec_updated_df)
            else:
                spec_updated_df = released_profile
                update_spec_table(eachfile,spec_updated_df)
        else:
            if 'draft' in eachfile:
                spec_updated_df = draft_type
                update_spec_table(eachfile,spec_updated_df)
            else:
                spec_updated_df = released_type
                update_spec_table(eachfile,spec_updated_df)