import unittest
import unittest.mock as unitmock

from simplify_JSON import add_missing_properties

class Test_Add_Missing_Properties(unittest.TestCase):

    def test_add_missing_properties(self):
        # Load in test data
        data = {"@context":{"schema":"http://schema.org/",
                    "rdf":"http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                    "rdfs":"http://www.w3.org/2000/01/rdf-schema#",
                    "bioschemas":"http://discovery.biothings.io/view/bioschemas/"},
                "@graph":[
                    {
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
        result = add_missing_properties(data, 'ComputationalTool', '1.0-RELEASE')
        graph_data = result.get('@graph')
        keyList = list(graph_data[0].keys())
        self.assertTrue('schema:schemaVersion' in keyList, 'schema:schemaVersion needs to be added')
        self.assertEqual('https://bioschemas.org/profiles/ComputationalTool/1.0-RELEASE',graph_data[0]['schema:schemaVersion'])
        self.assertTrue('schema:additionalType' in keyList, 'schema:additionalType needs to be added')
        self.assertEqual('https://bioschemas.org/profiles#nav-release', graph_data[0]['schema:additionalType'])

if __name__ == "__main__":
    unittest.main()