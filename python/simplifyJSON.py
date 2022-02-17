import json
import logging
import pandas
import pathlib
import re # regex library
import requests

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

def replaceDotsInFilename(filename):
    # Replace `.` in filename with `-` except for final `.json`
    str = re.sub('\.(?!json$)', '-', filename)
    return str

def readJSONFile(url):
    logging.debug('Entering readJSONFile from %s' % url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            data = json.loads(r.text)
            logging.debug('Exiting readJSONFile – dictionary size %d' % len(data))
            return data
        else:
            logging.error('Got a %d error code from %s' % (r.status_code, url))
            raise Exception('Got a %d error code from %s' % (r.status_code, url))
    except requests.exceptions.RequestException as e:
        raise SystemExit(e)

def writeJSONFile(data, filename):
    logging.debug('Entering writeJSONFile() with dictionary size %d and filename %s' % (len(data), filename))
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    f.close()
    logging.debug('Exiting writeJSONFile')

def replace_nested_json_key(obj, key, newkey):
    """Recursively replace key/value in nested JSON."""
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

def replaceJSONLDKey(data):
    logging.debug('Entering replaceJSONLDKey() with ' + str(data))
    replacementStrings = {'@context': 'jsonld-context',
                        '@graph': 'jsonld-graph',
                        '@id': 'jsonld-id',
                        '@type': 'jsonld-type',
                        '$validation': 'jsonld-validation',
                        '$schema': 'jsonld-schema',
                        '$ref': 'jsonld-ref',
                        'rdfs:comment': 'rdfs-comment',
                        'rdfs:label': 'rdfs-label',
                        'rdfs:subClassOf': 'rdfs-subClassOf'}
    for k, v in replacementStrings.items():
        data = replace_nested_json_key(data, k, v)
    logging.debug('Exiting replaceJSONLDKey() with ' + str(data))
    return data

def processProfiles(script_path):
    logging.debug('Entering processProfiles() with %s' % script_path)
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
        json_data = readJSONFile(url)
        logging.info('Replacing JSON-LD keys')
        json_data = replaceJSONLDKey(json_data)
        new_filename = SCHEMA_TARGET + replaceDotsInFilename(schema_file)
        logging.info('Writing data to %s' % new_filename)
        writeJSONFile(json_data, new_filename)
    logging.debug('Exiting processProfiles()')

#### Main
script_path = pathlib.Path(__file__).parent.absolute()
processProfiles(script_path)
print('SUCCESS! All profiles have been processed.\nCheck %s for the generated files.'
    % SCHEMA_TARGET)
