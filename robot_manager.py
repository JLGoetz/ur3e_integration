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
        # 1. Setup Logging FIRST so we can use it during hardware init
        self._setup_logging()
        
        self.ip = os.getenv("ROBOT_IP", "192.168.1.10")
        self.dash_port = 29123
        self.rt_control = None
        self.rt_receive = None
        self.is_connected = False
        
        # Joint Space Home Position (Radians)
        self.HOME_JOINTS = [0, -1.57, 1.57, -1.57, -1.57, 0]
        
        self.connect()

    def _setup_logging(self):
        self.logger = logging.getLogger("UR3e_Integrator")
        self.logger.setLevel(logging.INFO)
        # Avoid duplicate handlers if re-initialized
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

            log_file = "robot_operations.log"
            file_handler = RotatingFileHandler(
                log_file, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        self.logger.info("SYSTEM: Logging initialized.")

    def connect(self):
        """Initializes RTDE connection with internal retry/check."""
        try:
            self.logger.info(f"CONNECT: Attempting RTDE to {self.ip}...")
            # Using self.rt_control and self.rt_receive consistently
            self.rt_receive = rtde_receive.RTDEReceiveInterface(self.ip)
            self.rt_control = rtde_control.RTDEControlInterface(self.ip)
            self.is_connected = True
            self.logger.info("SUCCESS: RTDE Interfaces Synchronized.")
            return True
        except Exception as e:
            self.logger.error(f"RTDE Initialization failed: {e}")
            self.is_connected = False
            print(f"\n[!] CONNECTION ERROR: {e}")
            return False

    def dashboard(self, command):
        """Sends ASCII commands to the Dashboard Server (Port 29123)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((self.ip, self.dash_port))
                s.recv(1024) 
                s.sendall(f"{command}\n".encode())
                response = s.recv(1024).decode().strip()
                self.logger.info(f"DASHBOARD: Sent '{command}' | Recv: '{response}'")
                return response
        except Exception as e:
            self.logger.error(f"Dashboard Error: {e}")
            return None

    def power_on_sequence(self):
        print("Initiating Power On...")
        self.dashboard("power on")
        time.sleep(4.0) # Critical for C153 sync
        print("Releasing Brakes...")
        self.dashboard("brake release")

    def shutdown(self):
        self.dashboard("power off")
        self.logger.info("SYSTEM: Shutdown command sent.")

    def clear_faults(self):
        self.dashboard("unlock protective stop")
        self.dashboard("close safety popup")
        self.logger.info("SYSTEM: Fault recovery cleared.")

    def move_home(self):
        """Moves to home with standard safety checks."""
        if not self.is_connected:
            print("Error: Not connected to robot.")
            return

        # Check safety via rt_receive (matches init name)
        if not self.rt_receive.isRobotConnected():
            print("Aborted: Robot hardware is powered off.")
            return

        if self.rt_receive.isProtectiveStopped():
            print("Aborted: Robot is in Protective Stop.")
            return

        print("Moving to Home...")
        self.rt_control.moveJ(self.HOME_JOINTS, speed=1.0, acceleration=0.4)