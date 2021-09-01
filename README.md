## DDE Specifications maintainer
This script pulls json schema/validation files from specifications as listed in the specifications_list file and compiles them into a single update file for consumption/display by the DDE Schema Playground. It will automatically check for updates to the list of profiles and types, aggregate them and update them to the corresponding bioschemas namespace in the Data Discovery Engine

DO NOT EDIT the bioschemas.json file directly. Updates to this file will be over-written by the updates to the specification files listed in the specifications_list.txt file.

To update a specification, 
 1. copy the json file into the 'previous versions' folder and rename the file from:
    'current-RELEASE' to '{version number}-RELEASE'
 2. update the 'current-RELEASE.json' file for that specification in the corresponding specification folder/directory in the Bioschemas Specifications repository

To add a new specification to the DDE Schema Playground:
 1. add the new json schema file into an appropriate folder/directory within the Bioschemas Specifications repository and name it '{Class}_current-RELEASE.json', 
 2. update the specifications_list file with the url to the json file and the version
 
 
 



