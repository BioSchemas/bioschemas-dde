This python code takes the `JSON` output of the Data Discovery Engine and converts the JSON-LD files into a form that Jekyll can process. The script generates `html` files that contain the `yaml` frontmatter to display the profile.

## Source

To setup your environment run
```sh
pip install -r requirements.txt
```

To run the script just type `python simplify_JSON.py`. This will process the configuration file found on GitHub and save the resulting files `/schemas/`. Log messages are written to `simplifyJSON.log`.

## Tests

Unit tests have been written and can be found in the `tests` directory. The unittests can be run with the command
```bash
python -m unittest discover -s tests
```
