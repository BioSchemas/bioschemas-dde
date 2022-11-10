import json
import requests
import pandas as pd
from pandas import read_csv
import os
import pathlib
from datetime import datetime
from datetime import timedelta
from src.common import *

#### Main
script_path = pathlib.Path(__file__).parent.absolute()
run_update(script_path,False)