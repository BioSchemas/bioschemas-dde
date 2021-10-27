# DDE Specifications maintainer for bioschemas
This script pulls json schema/validation files from specifications as listed in the specifications_list file and compiles them into a single update file for consumption/display by the DDE Schema Playground. It will automatically check for updates to the list of profiles and types, aggregate them and update them to the corresponding bioschemas namespace in the Data Discovery Engine

DO NOT EDIT the bioschemas.json file directly. Updates to this file will be over-written by the updates to the specification files listed in the specifications_list.txt file.

### To update a specification via github:
 0. Fork the bioschemas specification repository
 1. Go to the specification folder of interest
 2. move the json file into the 'previous versions' folder 
 3. add your updated json specification to the top level of the appropriate specification folder and  name it '{Class}_{version}-RELEASE.json'

### To update a specification via the DDE:
 1. Go to https://discovery.biothings.io/registry
 2. Search for "bioschemas"
 3. Select the existing bioschema profile/type that you'd like to update
 4. Click on the "extend" icon
 5. Select all the properties that you'd like to keep
 6. Add new properties as needed
 7. Toggle the validation editor and add validation for any new properties. Also, edit validations for existing properties if there was a change in the cardinality, marginality, expected types, or allowed vocabularies
 8. Download/export your updated schema jsonld file to your desktop or to github
 9. Move a copy of it into the appropriate bioschemas specification folder (see "To update a specification via github)
 
 ### To test a new or updated specification:
 1. Fork the bioschemas_DDE repository
 2. Edit the specifications_list file (see below) <-- This will trigger the generation of the bioschemas.json file via github actions
 3. Go to https://discovery.biothings.io/schema-playground and click on "Register Schema" (don't worry, you won't be registering anything). Paste the link to YOUR generated bioschemas.json file into the schema viewer and click `Let's go`
 4. Click on the specification you updated to review how it appears in the DDE.
 5. Edit/iterate as needed. If you are satisfied with your specification, push your specifications_list file to the bioschemas_DDE repository

### To create a new specification to the DDE Schema Playground:
 1. If using the DDE Schema Playground to create the new specification, you will not be able to use the `bioschemas` namespace. This is fine, as the aggregator has a function for handling this. Just be sure to include the temporary namespace in the specifications_list file.
 2. add the new json schema file into an appropriate folder/directory within the Bioschemas Specifications repository and name it '{Class}_{version}-RELEASE.json'
 3. IMPORTANT--This should step should be done AFTER the new json schema file has been created. Better yet, load it with the DDE schema viewer to ensure that it is working as expected. If everything is working, update the specifications_list file (in this repository) with the url to the json file and other requested information. Note that this file is tab-delimited
 
 ## Caveats when working with the DDE Schema Playground:
 1. The DDE Schema Playground is strict when adhering to schema.org standards. Hence, properties must follow the schema.org naming conventions to work properly. You will be able to create properties which have non-standard names; HOWEVER, such properties will trigger errors when you try to view your schema in the schema viewer.
 2. If the expected type is a bioschemas type or profile, you should manually enter "bioschemas:{type/profile}. This will allow the property to properly reference the expected class in the greater schema. That said, IF the type/profile being referenced is NOT yet available in the DDE, this will cause an error. You can bypass this issue by creating a dummy/placeholder class for the referenced class in your specification. The specification merger has a handler for tossing these dummy/placeholder classes prior to merging.
 
 
 



