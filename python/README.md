This python code takes the output of the Data Discovery Engine and converts the JSON-LD files into a form that Jekyll can process. Specifically, it
- Renames the file: replacing `.` with `-`
- Replaces the following sequences within the JSON file:
    - `@id` → `jsonld-id`
    - `@graph` → `jsonld-graph`
    - `@context` → `jsonld-context`
    - `@type` → `jsonld-type`
    - `$validation` → `jsonld-validation`
    - `$schema` → `jsonld-schema`
    - `$ref` → `jsonld-ref`
    - `rdfs:comment` → `rdfs-comment`
    - `rdfs:label` → `rdfs-label`
    - `rdfs:subClassOf` → `rdfs-subClassOf`

## Source

To run the script just type `python simplify_JSON.py`. This will process the configuration file found on GitHub and save the resulting files `/schemas/`. Log messages are written to `simplifyJSON.log`.

## Tests

Unit tests have been written and can be found in the `tests` directory. The unittests can be run with the command
```bash
python -m unittest discover -s tests
```
