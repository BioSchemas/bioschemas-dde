# DDE Specifications maintainer for bioschemas
This script pulls json schema/validation files from specifications as listed in the specifications_list file and compiles them into a single update file for consumption/display by the DDE Schema Playground. It will automatically check for updates to the list of profiles and types, aggregate them and update them to the corresponding bioschemas namespace in the Data Discovery Engine

DO NOT EDIT the bioschemas.json file directly. Updates to this file will be over-written by the updates to the specification files listed in the specifications_list.txt file.

### To update a specification via github:
 1. Fork the bioschemas specification repository
 2. Go to the specification folder of interest
 4. add your updated json specification to the jsonld folder of the appropriate specification folder and  name it '{Class}_{version}-RELEASE.json' or '{Class}_{version}-DRAFT.json'. Deprecated specifications should be named '{Class}_{version}-DEPRECATED.json'.

### To update a specification via the DDE:
 1. Go to https://discovery.biothings.io/registry
 2. Search for "bioschemas". There are several version of bioschemas in the DDE. Be sure to start with the one that's most appropriate for your purpose:
    * `bioschemas` - Will give you the most recent RELEASED version of a PROFILE
    * `bioschemasdrafts` - Will give you the most recent DRAFT version of a PROFILE
    * `bioschemastypes` - Will give you the most recent RELEASED version of a TYPE
    * `bioschemastypesdrafts` - Will give you the most recent DRAFT version of a TYPE
    * `bioschemasdeprecated` - Will give you the most recent version of a DEPRECATED class (PROFILE or TYPE)     
 3. Select the existing bioschema profile/type that you'd like to update
 4. Click on the "extend" icon (note that you will have to use a temporary namespace, like 'bioschemastemp')
 5. Select all the properties that you'd like to keep
 6. Add new properties as needed
 7. Toggle the validation editor and add validation for any new properties. Also, edit validations for existing properties if there was a change in the cardinality, marginality, expected types, or allowed vocabularies. 
 8. Download/export your updated schema jsonld file to your desktop or to github
 9. If you'd like, you can use a simple text editor to do a simple find/replace and change your temporary namespace to 'bioschemas' (This is not necessary, as automated merging script can do this for you, but you will have to ensure you use the temporary namespace instead of 'bioschemas' if you do not follow this step). **Note that if you are creating or editing a type, you will need to DELETE the $validation section created by the DDE**
 10. Move a copy of it into the appropriate bioschemas specification folder (see "To update a specification via github)
 
 ### To test a new or updated specification:
 1. Fork the bioschemas_DDE repository
 2. Edit the appropriate file in your fork<-- This will trigger the generation of the json files via github actions in your fork of the repository (note that if your schema used a temporary namespace, you should use that namespace in the specification file, so the script does a proper replacement in the merged bioschemas.json). The file names are as follows:
     * `profile_list.txt`: All RELEASED PROFILES in this list will be added to the `bioschemas.json` (`bioschemas` namespace)
     * `draft_profile_list`:  All DRAFT PROFILES in this list will be added to the `bioschemasdrafts.json` (`bioschemasdrafts` namespace)
     *`type_list.txt`:  All RELEASED TYPES in this list will be added to the `bioschemastypes.json` (`bioschemastypes` namespace)
     *`draft_type_list.txt`: All DRAFT Types in this list will be added to the `bioschemastypesdrafts.json` (`bioschemastypesdrafts` namespace)
     *`deprecated.txt`: ALL DEPRECATED classes (PROFILES or TYPES) in this list will be added to the `bioschemasdeprecated.json` (`bioschemasdeprecated` namespace)
 3. Go to https://discovery.biothings.io/schema-playground and click on "Register Schema" (don't worry, you won't be registering anything). Paste the link to YOUR generated bioschemas.json file into the schema viewer and click `Let's go`
 4. Click on the specification you updated to review how it appears in the DDE.
 5. Edit/iterate as needed. If you are satisfied with your specification, push your updates to the bioschemas_DDE repository

### To create a new specification to the DDE Schema Playground:
 1. If using the DDE Schema Playground to create the new specification, you will not be able to use the reserved bioschemas namespaces. These namespaces include: `bioschemas` (released profiles), `bioschemasdrafts` (draft profiles), `bioschemastypes` (released types), `bioschemastypesdrafts` (draft types), and `bioschemasdeprecated` (deprecated profiles and types). This is fine, as the aggregator has a function for handling this. Just be sure to include the temporary namespace in the specifications_list file.
 2. add the new json schema file into an appropriate folder/directory within the Bioschemas Specifications repository and name it `{Class}_{version}-{RELEASE or DRAFT}.json` (If a class is deprecated, include the term {DEPRECATED}
 3. IMPORTANT--This should step should be done AFTER the new json schema file has been created. Better yet, load it with the DDE schema viewer to ensure that it is working as expected. If everything is working, update the appropriate list file (in this repository) with the url to the json file and other requested information. Note that the list files are tab-delimited
 
 ## Caveats when working with the DDE Schema Playground:
 1. The DDE Schema Playground is strict when adhering to schema.org standards. Hence, properties must follow the schema.org naming conventions to work properly. You will be able to create properties which have non-standard names; HOWEVER, such properties will trigger errors when you try to view your schema in the schema viewer.
 2. If the expected type is a bioschemas type or profile, you should manually enter "{namespace}:{Class name}". The namespace should be one of `bioschemas` (Released Profiles), `bioschemastypes` (Released Drafts), etc. This will allow the property to properly reference the expected class in the greater schema. That said, IF the type/profile being referenced is NOT yet available in the DDE, it will occassionaly cause an error. If that happens, you can bypass this issue by creating a dummy/placeholder class for the referenced class in your specification. 
 3. Although Bioschemas specifies `@id`, `@type`, `@context` as minimally required properties, these are properties required by jsonld and do not follow schema.org property naming conventions. For this reason, although they are required for all profiles and types, they cannot be included/viewed as properties within the DDE as they are requirements inherited from jsonld formatting and not schema.org
 4. Bioschemas also specifies `dct:conformsTo` as a minimally required property as a class. This will be automatically added to all classes via the merging script, so it should be omitted when creating a new specification or extending from an existing Bioschemas class.
 5. All defined classes will automatically have the schema version included. This will utilize the `schema:schemaVersion` property for which the value will be an array of versioned schemas referenced.
 
 
 



