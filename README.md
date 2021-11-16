# DDE Specifications maintainer for bioschemas
This script pulls json schema/validation files from specifications as listed in the specifications_list file and compiles them into a single update file for consumption/display by the DDE Schema Playground. It will automatically check for updates to the list of profiles and types, aggregate them and update them to the corresponding bioschemas namespace in the Data Discovery Engine

DO NOT EDIT the bioschemas.json file directly. Updates to this file will be over-written by the updates to the specification files listed in the specifications_list.txt file.

### To update a specification via github:
 1. Fork the bioschemas specification repository
 2. Go to the specification folder of interest
 4. add your updated json specification to the jsonld folder of the appropriate specification folder and  name it '{Class}_{version}-RELEASE.json' or '{Class}_{version}-Draft.json'

### To update a specification via the DDE:
 1. Go to https://discovery.biothings.io/registry
 2. Search for "bioschemas"
 3. Select the existing bioschema profile/type that you'd like to update
 4. Click on the "extend" icon (note that you will have to use a temporary namespace, like 'bioschemastemp')
 5. Select all the properties that you'd like to keep
 6. Add new properties as needed
 7. Toggle the validation editor and add validation for any new properties. Also, edit validations for existing properties if there was a change in the cardinality, marginality, expected types, or allowed vocabularies
 8. Download/export your updated schema jsonld file to your desktop or to github
 9. If you'd like, you can use a simple text editor to do a simple find/replace and change your temporary namespace to 'bioschemas' (This is not necessary, as automated merging script can do this for you, but you will have to ensure you use the temporary namespace instead of 'bioschemas' if you do not follow this step)
 10. Move a copy of it into the appropriate bioschemas specification folder (see "To update a specification via github)
 
 ### To test a new or updated specification:
 1. Fork the bioschemas_DDE repository
 2. Edit the specifications_list file (see below) in your fork<-- This will trigger the generation of the bioschemas.json file via github actions in your fork of the repository (note that if your schema used a temporary namespace, you should use that namespace in the specification file, so the script does a proper replacement in the merged bioschemas.json)
 3. Go to https://discovery.biothings.io/schema-playground and click on "Register Schema" (don't worry, you won't be registering anything). Paste the link to YOUR generated bioschemas.json file into the schema viewer and click `Let's go`
 4. Click on the specification you updated to review how it appears in the DDE.
 5. Edit/iterate as needed. If you are satisfied with your specification, push your specifications_list file to the bioschemas_DDE repository

### To create a new specification to the DDE Schema Playground:
 1. If using the DDE Schema Playground to create the new specification, you will not be able to use the `bioschemas` namespace. This is fine, as the aggregator has a function for handling this. Just be sure to include the temporary namespace in the specifications_list file.
 2. add the new json schema file into an appropriate folder/directory within the Bioschemas Specifications repository and name it '{Class}_{version}-RELEASE.json'
 3. IMPORTANT--This should step should be done AFTER the new json schema file has been created. Better yet, load it with the DDE schema viewer to ensure that it is working as expected. If everything is working, update the specifications_list file (in this repository) with the url to the json file and other requested information. Note that this file is tab-delimited
 
 ## Caveats when working with the DDE Schema Playground:
 1. The DDE Schema Playground is strict when adhering to schema.org standards. Hence, properties must follow the schema.org naming conventions to work properly. You will be able to create properties which have non-standard names; HOWEVER, such properties will trigger errors when you try to view your schema in the schema viewer.
 2. If the expected type is a bioschemas type or profile, you should manually enter "bioschemas:{type/profile}". This will allow the property to properly reference the expected class in the greater schema. That said, IF the type/profile being referenced is NOT yet available in the DDE, it will occassionaly cause an error. If that happens, you can bypass this issue by creating a dummy/placeholder class for the referenced class in your specification. The specification merger has a handler for tossing these dummy/placeholder classes prior to merging.
 3. Although Bioschemas specifies `@id`, `@type`, `@context` as minimally required properties, these are properties required by jsonld and do not follow schema.org property naming conventions. For this reason, although they are required for all profiles and types, they cannot be included/viewed as properties within the DDE as they are requirements inherited from jsonld formatting and not schema.org
 4. Bioschemas also specifies `dct:conformsTo` as a minimally required property as a class. This will be automatically added to all classes via the merging script, so it should be omitted when creating a new specification.
 5. All defined classes will automatically have the schema version included. This will utilize the `schema:schemaVersion` property for which the value will be an array of versioned schemas referenced.
 
 
 



