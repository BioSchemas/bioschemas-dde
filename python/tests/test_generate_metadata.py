import unittest

from simplify_JSON import generate_metadata

class Test_generate_metadata(unittest.TestCase):
    def test_generate_profile_metadata(self):
        """
        Test correct generation of profile metadata
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

        result = generate_metadata(data)
        self.assertEqual(result.get('layout'), 'Profile', 'Layout needs to be set to `Profile`')
        self.assertTrue('previous_version' in result, 'previous_version needs to be set')
        self.assertIsNone(result.get('previous_version'), 'previous_version needs to be empty')
        self.assertTrue('previous_release' in result, 'previous_release needs to be set')
        self.assertIsNone(result.get('previous_release'), 'previous_release needs to be empty')
        self.assertTrue('group' in result, 'group needs to be set')
        self.assertIsNone(result.get('group'), 'previous_release needs to be empty')


if __name__ == "__main__":
    unittest.main()
