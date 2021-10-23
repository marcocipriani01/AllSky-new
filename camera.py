#!/usr/bin/python3
import os
import json
import logging

class Camera:
    config = None
    night_mode = False
    capture_delay = 0

    def __init__(self, name, config_file):
        self.name = name
        self.logger = logging.getLogger(name)
        self.config_file = config_file

    def load_config(self):
        self.logger.info("Loading settings...")
        with open(self.config_file) as f:
            self.config = json.load(f)
        file = "./config/" + self.config_file
        if os.path.exists(file):
            with open(file) as f:
                self.config = json.load(f)
        else:
            logging.info("Loading default configuration.")
            with open("./config_default/" + self.config_file) as f:
                self.config = json.load(f)

    def get_capture_delay(self):
        return self.capture_delay

    def set_night_mode(self, night_mode):
        self.logger.info("Setting night mode to %s..." % night_mode)
        self.night_mode = night_mode

    def connect(self):
        if self.config is None:
            raise Exception("Camera not configured.")
        self.logger.info("Connecting to %s..." % self.name)

    def capture(self, output_file):
        if self.config is None:
            raise Exception("Camera not configured.")

    def disconnect(self):
        self.logger.info("Disconnecting...")
