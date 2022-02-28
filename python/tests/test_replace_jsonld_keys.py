import unittest
import unittest.mock as unitmock

import os
from simplify_JSON import replace_JSONLD_key

class Test_Replase_JSONLD_Keys(unittest.TestCase):

    def test_replace_JSONLD_Keys(self):
        """
        Test that json-ld strings are converted to regular keys
        """
        # Load in test data
        data = {"@context":{"schema":"http://schema.org/",
                    "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
                    "bioschemas":"http://discovery.biothings.io/view/bioschemas/"},
                "@graph":[
                    {
                        "schema:schemaVersion": "1.0-RELEASE",
                        "schema:additionalType": "https://bioschemas.org/profiles#nav-release",
                        "@id":"bioschemas:ComputationalTool",
                        "@type":"rdfs:Class",
                        "rdfs:comment":"Some comment. Version 1.0-RELEASE.",
                        "rdfs:label":"ComputationalTool",
                        "rdfs:subClassOf":{
                            "@id":"schema:SoftwareApplication"},
                        "$validation":{
                            "$schema":"http://json-schema.org/draft-07/schema#",
                            "type":"object",
                            "input":{
                                "description":"Specification of a consumed input.",
                                "oneOf":[{
                                    "$ref":"#/definitions/formalParameter"},
                                    {"type":"array",
                                        "items":{"$ref":"#/definitions/formalParameter"}
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "schema:domainIncludes": {
                            "jsonld-id": "bioschemas:ComputationalTool"
                        },
                        "schema:rangeIncludes": [
                            {
                                "jsonld-id": "schema:URL"
                            }
                        ],
                        "jsonld-id": "bioschemas:codeRepository",
                        "jsonld-type": "rdf:Property",
                        "rdfs-comment": "Link to the source code repository of the tool.",
                        "rdfs-label": "codeRepository"
                    }
                ]}

        result = replace_JSONLD_key(data)
        keyList = list(result.keys())
        self.assertEqual(keyList[0], 'jsonld-context')
        self.assertEqual(keyList[1], 'jsonld-graph')

        graph_data = result.get('jsonld-graph')
        keyList = list(graph_data[0].keys())
        self.assertTrue('schema-additionalType' in keyList, 'schema:additionalType needs to be converted')
        self.assertTrue('schema-schemaVersion' in keyList, 'schema:schemaVersion needs to be converted')
        self.assertTrue('jsonld-id' in keyList, 'jsonld-id not in keys')
        self.assertTrue('jsonld-type' in keyList, 'jsonld-type not in keys')
        self.assertTrue('jsonld-validation' in keyList, 'jsonld-validation not in keys')

        subKeyList = list(graph_data[0].get('jsonld-validation'))
        self.assertTrue('jsonld-schema' in subKeyList, 'jsonld-schema not in keys')
        self.assertTrue('input' in subKeyList, 'input not in keys – should be unchanged from source data')
        self.assertTrue('type' in subKeyList, 'type not in keys – should be unchanged from source data')

        self.assertTrue('jsonld-ref' in graph_data[0].get('jsonld-validation').get('input').get('oneOf')[0].keys(), 'jsonld-ref not in keys')
        self.assertTrue('rdfs-comment' in keyList, 'rdfs-comment not in keys')
        self.assertTrue('rdfs-label' in keyList, 'rdfs-label not in keys')
        self.assertTrue('rdfs-subClassOf' in keyList, 'rdfs-subClassOf not in keys')

        keyList = list(graph_data[1].keys())
        self.assertTrue('schema-domainIncludes' in keyList, 'schema:domainIncludes should be converted')
        self.assertTrue('schema-rangeIncludes' in keyList, 'schema:rangeIncludes should be converted')

if __name__ == "__main__":
    unittest.main()
