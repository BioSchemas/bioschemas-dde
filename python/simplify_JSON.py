import json
import logging
import pandas
import pathlib
import re # regex library
import requests
import yaml

## Logging configuration
logging.basicConfig(
    filename='simplifyJSON.log',
    filemode='w',
    encoding='utf-8',
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO)

### GLOBAL CONSTANTS
# Define location to read DDE generated JSON files
SCHEMA_SOURCE = "https://raw.githubusercontent.com/BioSchemas/specifications/master/"
# Define location to write simplified JSON Schema files
SCHEMA_TARGET = "schemas/"

def rename_file(filename):
    """
    Rename the supplied filename so that any `.` in the filename are 
    replaced with `-`. Replace the `.json` file ending with `.yml`. 
    This will allow Jekyll to open the file.
    """
    logging.debug('Entering rename_file() with %s' % filename)
    # Replace `.` in filename with `-` except for final `.json`
    str = re.sub('\.(?!json$)', '-', filename)
    str = str.replace('.json', '.yml')
    logging.debug('Exiting rename_file() with %s' % str)
    return str

def read_JSON_file(url):
    """
    Read in the contents of the JSON file located at the supplied URL.    
    """
    logging.debug('Entering read_JSON_file from %s' % url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = json.loads(r.text)
            logging.debug('Exiting read_JSON_file – dictionary size %d' % len(data))
            return data
        else:
            logging.error('Got a %d error code from %s' % (r.status_code, url))
            raise Exception('Got a %d error code from %s' % (r.status_code, url))
    except requests.exceptions.RequestException as e:
        logging.error('Bad request: ' + e)
        raise SystemExit(e)

def write_YAML_file(data, filename):
    logging.debug('Entering write_YAML_file() with dictionary size %d and filename %s' % (len(data), filename))
    with open(filename, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)
    f.close()
    logging.debug('Exiting write_YAML_file()')

def generate_metadata(data):
    logging.debug('Entering generate_metadata() with ' + str(data))
    metadata = {'layout': 'Profile', 
                'previous_version': None, 
                'previous_release': None,
                'group': None,
                'changes': None}
    logging.debug('Exiting generate_metadata() with ' + str(metadata))
    return metadata

def replace_nested_json_key(obj, key, newkey):
    """Recursively replace key in nested JSON."""
    logging.debug("Entering replace_nested_json_key() with key: %s, newkey: %s, and dict:\n%s" % (key, newkey, str(obj)))
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)):
                replace_nested_json_key(v, key, newkey)
        if key in obj:
            logging.debug('Replacing %s with %s' % (key, newkey))
            obj[newkey] = obj.pop(key)
    elif isinstance(obj, list):
        for item in obj:
            replace_nested_json_key(item, key, newkey)

    logging.debug("Exiting replace_nested_json_key() with key: %s, newkey: %s, and dict:\n%s" % (key, newkey, str(obj)))
    return obj

def replace_JSONLD_key(data):
    """
    Replace the JSONLD/JSON-Schema specific keys with values that 
    Jekyll's JSON processor can handle. 
    The set of replacements is defined in the replacement_strings dict
    """
    logging.debug('Entering replace_JSONLD_key() with ' + str(data))
    replacement_strings = {'@context': 'jsonld-context',
                        '@graph': 'jsonld-graph',
                        '@id': 'jsonld-id',
                        '@type': 'jsonld-type',
                        '$validation': 'jsonld-validation',
                        '$schema': 'jsonld-schema',
                        '$ref': 'jsonld-ref',
                        'rdfs:comment': 'rdfs-comment',
                        'rdfs:label': 'rdfs-label',
                        'rdfs:subClassOf': 'rdfs-subClassOf',
                        'schema:additionalType': 'schema-additionalType',
                        'schema:schemaVersion': 'schema-schemaVersion',
                        'schema:domainIncludes': 'schema-domainIncludes',
                        'schema:rangeIncludes': 'schema-rangeIncludes'}
    for k, v in replacement_strings.items():
        data = replace_nested_json_key(data, k, v)
    logging.debug('Exiting replace_JSONLD_key() with ' + str(data))
    return data

def add_profile_status(version):
    """
    Add whether the profile is draft, release, or deprecated 
    """
    logging.debug('Entering add_profile_status() with ' + version)
    base_url = 'https://bioschemas.org/profiles#nav-'
    if 'deprecated' in version.lower():
        status = base_url + 'deprecated'
    elif 'release' in version.lower():
        status = base_url + 'release'
    elif 'draft' in version.lower():
        status = base_url + 'draft'
    logging.debug('Exiting add_profile_status() with ' + status)
    return status

def add_schemaVersion(profile, version):
    """
    Add the corresponding schema:schemaVersion property
    """
    logging.debug('Entering add_schemaVersion() with profile name %s and version number %s' % (profile, version))
    version = "https://bioschemas.org/profiles/" + profile + '/' + version
    logging.debug('Exiting add_schemaVersion() with ' + version)
    return version

def add_missing_properties(data, profile, version):
    """
    Add properties that are missing when JSON-Schema is written out by DDE
    """
    logging.debug('Entering add_missing_properies() with ' + str(data))
    graph_data = data["@graph"][0]
    # print(graph_data.keys())
    graph_data.update({'schema:schemaVersion': add_schemaVersion(profile, version)})
    graph_data.update({'schema:additionalType': add_profile_status(version)})
    data["@graph"][0] = graph_data
    logging.debug('Exiting add_missing_properties() with ' + str(data))
    return data

def process_profiles(script_path):
    """
    Read the specifications_list file stored on GitHub. Iterate through each
    profile in the file and generate a new schema file that Jekyll's JSON
    processor can handle.
    """
    logging.debug('Entering process_profiles() with %s' % script_path)
    # Read profile details in from file
    profiles = pandas.read_csv('../specifications_list.txt',
                delimiter='\t',
                header=0,
                usecols=["name","version"])
    # Process each profile in turn
    for index, row in profiles.iterrows():
        profile = row['name']
        release = row['version']
        logging.info('Processing %s release %s' % (profile, release))
        schema_file = profile + '_v' + release + '.json'
        url = SCHEMA_SOURCE + profile + "/jsonld/" + schema_file
        logging.info('Retrieving file from %s' % url)
        json_data = read_JSON_file(url)
        logging.info('Adding missing properties')
        json_data = add_missing_properties(json_data, profile, release)
        logging.info('Replacing JSON-LD keys')
        json_data = replace_JSONLD_key(json_data)
        new_filename = SCHEMA_TARGET + rename_file(schema_file)
        logging.info('Writing data to %s' % new_filename)
        write_YAML_file(json_data, new_filename)
    logging.debug('Exiting process_profiles()')

#### Main
if __name__ == "__main__":
    script_path = pathlib.Path(__file__).parent.absolute()
    process_profiles(script_path)
    print('SUCCESS! All profiles have been processed.\nCheck %s for the generated files.'
        % SCHEMA_TARGET)
