import json
import requests
import pandas as pd
import os
import pathlib
from src.metatables import *

#### Main
script_path = pathlib.Path(__file__).parent.absolute()
update_tables(script_path)