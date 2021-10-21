#!/usr/bin/python3
import sys
# Let's get this out of the way
if __name__ != "__main__":
    print("Can't run as a library.")
    sys.exit()

# Important imports
import os
import locale
import logging
import argparse
import datetime
from pathlib import Path
# Settings
import json

# Work in the right directory
global pwd
pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(pwd)

# Command line arguments
parser = argparse.ArgumentParser(description="AllSky capture software.")
parser.add_argument('-v', action='store_true', help="Verbose logging")

args = parser.parse_args()

# Logging
if args.v:
    logging.basicConfig(filename='./debug.log', level=logging.INFO, filemode='a')
else:
    logging.basicConfig(filename='./debug.log', level=logging.ERROR, filemode='a')
logging.info("AllSky started @" + datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss'))

def load_defaults():
    global config
    """Load the default settings"""
    with open("./config/default.json") as fin:
        config = json.load(fin)
    dir = pwd
    if not dir.endswith(os.sep):
        dir += os.sep
    dir += "images"
    Path(dir).mkdir(parents=False, exist_ok=True)
    config["Images folder"] = dir

global config
# Load configuraton
if os.path.exists("./config/config.json"):
    try:
        with open("./config/config.json") as fin:
            config = json.load(fin)
    except:
        logging.exception("Couldn't load config file, using default.")
        load_defaults()
else:
    logging.info("Loading default configuration.")
    load_defaults()

# Set locale
try:
    locale.setlocale(locale.LC_TIME, config["Global settings"]["Locale"])
except:
    logging.warning("Couldn't set locale, ignoring.")

