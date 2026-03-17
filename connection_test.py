import rtde_receive
import rtde_control
import time
import os
from dotenv import load_dotenv
load_dotenv()


# --- Configuration ---
ROBOT_IP = os.getenv("ROBOT_IP")  # Replace with your UR5e IP

def verify_connection():
    try:
        print(f"Connecting to UR5e at {ROBOT_IP}...")
        
        # Initialize RTDE Interfaces
        # rtde_receive: Pulls 500Hz data from the robot
        # rtde_control: Sends commands to the robot
        rtde_r = rtde_receive.RTDEReceiveInterface(ROBOT_IP)
        rtde_c = rtde_control.RTDEControlInterface(ROBOT_IP)
        
        print("Connected successfully.\n")

        # 1. Safety Check (Critical for Industrial Standards)
        # Check if the robot is in a state capable of receiving commands
        if rtde_r.isProtectiveStopped():
            print("ALERT: Robot is in a Protective Stop!")
            return
        
        if rtde_r.isEmergencyStopped():
            print("ALERT: Emergency Stop is engaged!")
            return

        # 2. Data Verification (Read)
        # Getting actual TCP Pose in Base Frame
        actual_tcp_pose = rtde_r.getActualTCPPose()
        print("--- Telemetry Verification ---")
        print(f"Actual TCP Pose: {actual_tcp_pose}")
        print(f"Joint Temperatures: {rtde_r.getJointTemperatures()}°C")
        
        # 3. Communication Latency/Sync Check
        # We check if the robot's timestamp is incrementing
        t_start = rtde_r.getTimestamp()
        time.sleep(0.1)
        t_end = rtde_r.getTimestamp()
        
        if t_end > t_start:
            print(f"Sync Verified: Data packet delta is {t_end - t_start:.4f}s")
        
        # 4. Command Verification (Write)
        # We use a moveJ to the current position (no actual movement) 
        # to verify the control socket is open.
        print("\nVerifying Control Socket...")
        current_joints = rtde_r.getActualQ()
        success = rtde_c.moveJ(current_joints, speed=0.1, acceleration=0.1)
        
        if success:
            print("Control Command Accepted: Bidirectional communication confirmed.")
        else:
            print("Control Command Rejected: Check robot mode (must be in Remote Control).")

    except Exception as e:
        print(f"Connection Failed: {e}")
        print("\nTroubleshooting Tip: Ensure the PC is on the same subnet (e.g., 192.168.1.x) "
              "and the UR5e 'Remote Control' mode is enabled on the TP.")
    
    finally:
        # Cleanly close the threads
        if 'rtde_r' in locals(): rtde_r.disconnect()
        if 'rtde_c' in locals(): rtde_c.disconnect()
        print("\nInterfaces disconnected.")

if __name__ == "__main__":
    verify_connection()