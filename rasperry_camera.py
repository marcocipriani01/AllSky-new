#!/usr/bin/python3
from camera import Camera
from picamera import PiCamera

class RaspberryCamera(Camera):
    camera = None
    camera_num = -1

    def __init__(self):
        super().__init__("picamera", "picamera.json")

    def connect(self):
        super().connect()
        number = self.config["camera_number"]
        if self.camera_num != number:
            self.disconnect()
        if self.camera is None:
            self.camera = PiCamera(camera_num=number)
            self.camera_num = number
            if self.camera.revision != "imx477":
                raise Exception("Only the Raspberry HQ camera is supported!")
        width = self.config["width"]
        if width == 0:
            width = self.camera.MAX_RESOLUTION.width
        height = self.config["height"]
        if height == 0:
            height = self.camera.MAX_RESOLUTION.height
        self.camera.resolution = (width, height)
        self.camera.vflip = self.config["mirror_vertical"]
        self.camera.hflip = self.config["mirror_horizontal"]
        self.camera.rotation = self.config["rotation"]
        self.camera.saturation = self.config["saturation"]
        self.camera.contrast = self.config["contrast"]
        self.camera.brightness = self.config["brightness"]
        if self.config["crop"]:
            self.camera.zoom = (
                self.config["crop_x"] / width,
                self.config["crop_y"] / height,
                self.config["crop_width"] / width,
                self.config["crop_height"] / height
            )
        else:
            self.camera.zoom = (0.0, 0.0, 1.0, 1.0)
        if self.config["auto_white_balance"]:
            self.camera.awb_mode = "auto"
        else:
            self.camera.awb_mode = "off"
            self.camera.awb_gains = (
                self.config["white_balance_red"],
                self.config["white_balance_blue"]
            )

    def capture(self, output_file):
        super().capture(output_file)
        if self.night_mode:
            settings = self.config["night"]
        else:
            settings = self.config["day"]
        delay = settings["delay"]
        try:
            delay = float(delay) * 1000
        except ValueError:
            if delay.endswith("ms"):
                delay = float(delay[:-2])
            elif delay.endswith("s"):
                delay = float(delay[:-1]) * 1000
            elif delay.endswith("m"):
                delay = float(delay[:-1]) * 60000
            elif delay.endswith("h"):
                delay = float(delay[:-1]) * 3600000
        self.capture_delay = delay
        self.camera.sensor_mode = settings["sensor_mode"]
        exposure = settings["exposure"]
        if exposure == 0.0:
            self.camera.exposure_mode = "auto"
            self.logger.info("Capturing with automatic exposure time...")
        else:
            self.camera.exposure_mode = "off"
            self.logger.info("Capturing with exposure time %0.2fs..." % exposure)
        self.camera.shutter_speed = exposure
        self.camera.iso = settings["iso"]
        self.camera.capture(output_file, format="jpeg", quality=self.config["jpg_quality"])

    def disconnect(self):
        super().disconnect()
        if self.camera is not None:
            self.camera.close()
            self.camera = None
