#!/usr/bin/python3
import sys
# Let's get this out of the way
if __name__ != "__main__":
    print("Can't run as a library.")
    sys.exit()

import os
import json
import locale
import logging
import argparse
import datetime
from time import sleep
from pathlib import Path

# Work in the right directory
global pwd
pwd = os.path.dirname(os.path.abspath(__file__))
os.chdir(pwd)

# Command line arguments
parser = argparse.ArgumentParser(description="AllSky capture software.")
parser.add_argument('-v', action='store_true', help="Verbose logging")
args = parser.parse_args()

def load_defaults():
    """Load the default settings"""
    global config
    with open("./config_defaults/default.json") as f:
        config = json.load(f)
    dir = pwd
    if not dir.endswith(os.sep):
        dir += os.sep
    dir += "images"
    Path(dir).mkdir(parents=False, exist_ok=True)
    config["folder"] = dir

global config
# Load configuraton
if os.path.exists("./config/config.json"):
    try:
        with open("./config/config.json") as f:
            config = json.load(f)
    except:
        logging.exception("Couldn't load config file, using default.")
        load_defaults()
else:
    logging.info("Loading default configuration.")
    load_defaults()

# Logging
if args.v or config["debug"]:
    logging.basicConfig(filename='./debug.log', level=logging.INFO, filemode='a')
else:
    logging.basicConfig(filename='./debug.log', level=logging.ERROR, filemode='a')
logging.info("AllSky started @" + datetime.datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss'))

# Set locale
try:
    locale.setlocale(locale.LC_TIME, config["locale"])
except:
    logging.warning("Couldn't set locale, ignoring.")

global camera
if config["camera"] == "picamera":
    from rasperry_camera import RaspberryCamera
    camera = RaspberryCamera()
else:
    # TODO: Add support for other cameras
    raise Exception("Unknown camera type.")

camera.load_config()
output_file = config["folder"]
if not output_file.endswith(os.sep):
    output_file += os.sep
output_file += config["filename"]

while True:
    camera.capture(output_file)
    sleep(camera.get_capture_delay())
