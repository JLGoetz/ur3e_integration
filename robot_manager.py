import rtde_control
import rtde_receive
import logging
import socket
import time
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

class UR3eManager:
    def __init__(self):
        self.ip = os.getenv("ROBOT_IP", "192.168.1.10")
        self._setup_logging()
        
        self.rt_control = None
        self.rt_receive = None
        self.is_connected = False
        
        # Joint Space Home Position (Radians)
        self.HOME_JOINTS = [0, -1.57, 1.57, -1.57, -1.57, 0]

    def _setup_logging(self):
        """Sets up a rotating log file with UTF-8 encoding for Windows compatibility."""
        self.logger = logging.getLogger("UR3e_Integrator")
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File Handler
        log_file = "robot_operations.log"
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        self.logger.info("SYSTEM: Logging initialized. Ready for operation.")

    def power_on_and_release_brakes(self):
        """Remote power on via Dashboard Server (Port 29123)."""
        try:
            self.logger.info("DASHBOARD: Connecting to Dashboard Server...")
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(10.0)
                s.connect((self.ip, 29123))
                s.recv(1024) # Connection string

                self.logger.info("DASHBOARD: Sending 'power on'...")
                s.sendall(b"power on\n")
                time.sleep(3)
                
                self.logger.info("DASHBOARD: Sending 'brake release'...")
                s.sendall(b"brake release\n")
                time.sleep(5)
                
                return True
        except Exception as e:
            self.logger.error(f"DASHBOARD: Power-on sequence failed: {e}")
            return False

    def power_on_and_release_brakes(self):
        """Sends commands to the Dashboard Server to prepare robot for motion."""
        import socket
        try:
            self.logger.info("DASHBOARD: Connecting to Dashboard Server (Port 29123)...")
            # Create a TCP socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                s.connect((self.ip, 29123))
                
                # UR Dashboard Server sends a 'Connected' message immediately
                s.recv(1024) 

                # 1. Power On
                self.logger.info("DASHBOARD: Sending 'power on'...")
                s.sendall(b"power on\n")
                time.sleep(2) # Allow time for electronics to stabilize
                
                # 2. Brake Release
                self.logger.info("DASHBOARD: Sending 'brake release'...")
                s.sendall(b"brake release\n")
                time.sleep(5) # Brakes take a few seconds to physically click open
                
                self.logger.info("SUCCESS: Robot powered on and brakes released.")
                return True
        except Exception as e:
            self.logger.error(f"DASHBOARD: Failed to power on robot: {e}")
            return False
        
    def connect(self):
        """Initializes RTDE connection."""
        try:
            self.logger.info(f"CONNECT: Attempting RTDE connection to {self.ip}...")
            self.rt_receive = rtde_receive.RTDEReceiveInterface(self.ip)
            self.rt_control = rtde_control.RTDEControlInterface(self.ip)
            self.is_connected = True
            self.logger.info("SUCCESS: RTDE Interfaces Synchronized.")
            return True
        except Exception as e:
            self.logger.error(f"FAILURE: RTDE Connection failed: {e}")
            return False

    def check_safety(self):
        """Verifies robot safety status."""
        if not self.is_connected:
            return False
        if self.rt_receive.isEmergencyStopped():
            self.logger.error("SAFETY: Emergency Stop Active.")
            return False
        if self.rt_receive.isProtectiveStopped():
            self.logger.warning("SAFETY: Protective Stop Active.")
            return False
        return True

    def move_to_home(self, speed=0.5, accel=0.5):
        """Executes a MoveJ to Home."""
        if not self.check_safety():
            return False

        self.logger.info(f"COMMAND: MoveJ to Home | Speed: {speed} | Accel: {accel}")
        try:
            self.rt_control.moveJ(self.HOME_JOINTS, speed, accel)
            self.logger.info("STATUS: Movement completed successfully.")
            return True
        except Exception as e:
            self.logger.error(f"STATUS: Movement failed: {e}")
            return False

    def disconnect(self):
        """Cleanly terminates session."""
        if self.rt_control:
            self.rt_control.stopScript()
            self.logger.info("SYSTEM: Session ended. Communication closed.")