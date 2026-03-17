from robot_manager import UR3eManager
import sys
import io

# Enforce UTF-8 for Windows console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def main():
    # Initialize the Manager
    robot = UR3eManager()
    
    # 1. Hardware Prep: Power on electronics and release mechanical brakes
    # This uses the Dashboard Server on Port 29123
    #if robot.power_on_and_release_brakes():
        
    # 2. Communication: Start the 500Hz RTDE synchronization
    if robot.connect():
        
        # 3. Execution: Move to the predefined Home position
        robot.move_to_home(speed=0.2, accel=0.1)
        
        # 4. Cleanup: Stop the RTDE control loop
        robot.disconnect()
    else:
        print("CRITICAL: Could not prepare robot hardware. Check Emergency Stop.")

if __name__ == "__main__":
    main()