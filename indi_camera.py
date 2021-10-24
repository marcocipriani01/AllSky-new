#!/usr/bin/python3
import logging
from camera import Camera
from PyIndi import BaseClient, ISS_ON as ON, ISS_OFF as OFF, IPS_IDLE as IDLE, IPS_OK as OK, IPS_BUSY as BUSY, IPS_ALERT as ALERT
from time import sleep, time
 
class INDICamera(BaseClient, Camera):
    camera = None
    connection_prop = None
    exposure_prop = None
    image_prop = None

    def __init__(self):
        Camera.__init__(self, "indi_camera", "indi.json")

    def newDevice(self, d):
        self.logger.info("New device " + d.getDeviceName())

    def newProperty(self, p):
        self.logger.debug("New property %s for device %s." % p.getName(), p.getDeviceName())

    def removeProperty(self, p):
        self.logger.debug("New property %s for device %s." % p.getName(), p.getDeviceName())

    def newBLOB(self, bp):
        pass

    def newSwitch(self, svp):
        pass

    def newNumber(self, nvp):
        pass

    def newText(self, tvp):
        pass

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        self.logger.info("INDI server connected event.")

    def serverDisconnected(self, code):
        self.logger.info("INDI server connected event (code = %d)." % code)

    def wait_for_switch_prop(self, property_name, timeout=5):
        start_time = now = time()
        property = self.camera.getSwitch(property_name)
        while not property and (now - start_time) <= timeout:
            sleep(0.5)
            now = time()
            property = self.camera.getSwitch(property_name)
        return property

    def wait_for_number_prop(self, property_name, timeout=5):
        start_time = now = time()
        property = self.camera.getNumber(property_name)
        while not property and (now - start_time) <= timeout:
            sleep(0.5)
            now = time()
            property = self.camera.getNumber(property_name)
        return property

    def wait_for_blob_prop(self, property_name, timeout=5):
        start_time = now = time()
        property = self.camera.getBLOB(property_name)
        while not property and (now - start_time) <= timeout:
            sleep(0.5)
            now = time()
            property = self.camera.getBLOB(property_name)
        return property

    def connect(self):
        Camera.connect(self)
        host = self.config["host"]
        port = self.config["port"]
        self.logger.info("Attempting connection to %s:%d..." % (host, port))
        self.setServer(host, port)
        driver_name = self.config["driver_name"]
        self.watchDevice(driver_name)
        if self.connectServer():
            self.logger.info("Connected to the INDI server. Waiting for camera.")
            start_time = now = time()
            while self.camera is None and (now - start_time) <= 5.0:
                sleep(0.5)
                now = time()
                self.camera = self.getDevice(driver_name)
            if self.camera is None:
                self.logger.error("Camera not found.")
                self.disconnect()
                return False
            self.logger.info("Camera found.")
            self.logger.info("Waiting for the connection property.")
            self.connection_prop = self.wait_for_switch_prop("CONNECTION")
            if not self.connection_prop:
                self.logger.error("Connection property not found.")
                self.disconnect()
                return False
            if not self.camera.isConnected():
                self.logger.info("Connecting camera...")
                for el in self.connection_prop.getSwitch():
                    logging.info("Setting property element %s to %s" % (el.label, ON if el.name == "CONNECT" else OFF))
                    el.s = ON if el.name == "CONNECT" else OFF
                self.sendNewSwitch(self.connection_prop)
                start_time = now = time()
                while self.connection_prop.getState() != OK and (now - start_time) <= 15.0:
                    sleep(0.5)
                    now = time()
            if self.connection_prop.getState() != OK:
                self.logger.error("Connection property not OK. Current state " + self.connection_prop.getStateAsString())
                self.disconnect()
                return False
            self.exposure_prop = self.wait_for_number_prop("CCD_EXPOSURE")
            if not self.exposure_prop:
                self.logger.error("Exposure property not found.")
                self.disconnect()
                return False
            self.image_prop = self.wait_for_blob_prop("CCD1")
            if not self.image_prop:
                self.logger.error("Image BLOB property not found.")
                self.disconnect()
                return False
            self.logger.info("INDI camera OK, all checks passed. Connected.")
            self.connected = True
            return True
        else:
            self.logger.error("Cannot connect to the INDI server.")
            return False

    def capture(self, output_file):
        Camera.capture(self, output_file)

    def disconnect(self):
        Camera.disconnect(self)
        if self.isServerConnected():
            self.disconnectServer()
        self.camera = None
        self.connection_prop = None
        self.exposure_prop = None
        self.image_prop = None
        self.connected = False

    def is_connected(self):
        return Camera.is_connected(self) and self.isServerConnected()
 
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cam = INDICamera()
    cam.load_config()
    cam.connect()
