This python code takes the `JSON` output of the Data Discovery Engine and converts the JSON-LD files into a form that Jekyll can process. The script generates `html` files that contain the `yaml` frontmatter to display the profile.

## Source

To setup your environment run
```sh
pip install -r requirements.txt
```

To run the script just type `python simplify_JSON.py`. This will process the configuration file found on GitHub and save the resulting files into subfolders under `/schemas/`. Log messages are written to `simplifyJSON.log`.

The generated folders in the `/schemas` directory can be copied across to the `/pages/_profiles/` directory in the website. Note that only the versions configured in the [online csv file](https://raw.githubusercontent.com/BioSchemas/specifications/master/) will be processed.

## Tests

Unit tests have been written and can be found in the `tests` directory. The unittests can be run with the command
```bash
python -m unittest discover -s tests
```
