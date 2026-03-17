import rtde_control
import rtde_receive
import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

load_dotenv()

class UR3eManager:
    def __init__(self):
        self.ip = os.getenv("ROBOT_IP", "192.168.1.10")
        self._setup_logging()
        
        self.rt_control = None
        self.rt_receive = None
        self.is_connected = False
        self.HOME_JOINTS = [0, -1.57, 1.57, -1.57, -1.57, 0]

    def _setup_logging(self):
        """Sets up a rotating log file and console output."""
        self.logger = logging.getLogger("UR3e_Integrator")
        self.logger.setLevel(logging.INFO)

        # Create format: Timestamp - Level - Message
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler (Rotates at 5MB, keeps 5 old logs)
        log_file = "robot_operations.log"
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        self.logger.info("Logging initialized. System ready.")

    def connect(self):
        try:
            self.logger.info(f"Attempting connection to {self.ip}...")
            self.rt_receive = rtde_receive.RTDEReceiveInterface(self.ip)
            self.rt_control = rtde_control.RTDEControlInterface(self.ip)
            self.is_connected = True
            self.logger.info("✅ RTDE Interfaces Synchronized.")
            return True
        except Exception as e:
            self.logger.error(f"❌ Connection Failed: {e}")
            return False

    def check_safety(self):
        if not self.is_connected:
            return False
        
        # Log safety violations as WARNING or ERROR
        if self.rt_receive.is_emergency_stopped():
            self.logger.error("EMERGENCY STOP DETECTED")
            return False
            
        if self.rt_receive.is_protective_stopped():
            self.logger.warning("PROTECTIVE STOP DETECTED - Check for collisions")
            return False

        return True

    def move_to_home(self, speed=0.5, accel=0.5):
        if not self.check_safety():
            return False

        self.logger.info(f"Command: MoveJ to Home | Speed: {speed} | Accel: {accel}")
        try:
            self.rt_control.moveJ(self.HOME_JOINTS, speed, accel)
            self.logger.info("Movement Completed: Robot at Home.")
            return True
        except Exception as e:
            self.logger.error(f"Movement Interrupted: {e}")
            return False

    def disconnect(self):
        if self.rt_control:
            self.rt_control.stopScript()
            self.logger.info("Session ended. Communication closed.")