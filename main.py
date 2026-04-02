from robot_manager import UR3eManager
import sys
import io


# Enforce UTF-8 for Windows console output
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def main():
    
    # Initialize the Manager
    robot = UR3eManager()
    
    print("\n--- UR5e ADMIN CONTROL ---")
    print("Commands: [on] [off] [clear] [home] [status] [exit]")

    while True:
        cmd = input("\nEnter Command: ").lower().strip()
        
        if cmd == "on":
            robot.power_on_sequence()
        elif cmd == "off":
            robot.shutdown()
        elif cmd == "clear":
            robot.clear_faults()
        elif cmd == "home":
            robot.move_home()
        elif cmd == "status":
            mode = robot.dashboard("robotmode")
            safety = robot.dashboard("safetymode")
            print(f"Robot Mode: {mode} | Safety Mode: {safety}")
        elif cmd == "exit":
            break
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()