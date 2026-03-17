import rtde_control
import rtde_receive
import sys

def check_installation():
    print(f"--- UR_RTDE Installation Check ---")
    print(f"Python Version: {sys.version}")
    
    try:
        # Check if we can access the module version
        # Note: some versions of ur_rtde don't expose __version__ directly 
        # but we can try to initialize a dummy interface
        print("Loading RTDE interfaces...")
        
        # This will fail with a Connection Error if no robot is found,
        # WHICH IS GOOD. It means the library is installed and trying to work.
        test_control = rtde_control.RTDEControlInterface("127.0.0.1")
        
    except RuntimeError as e:
        if "Could not connect" in str(e) or "Connection refused" in str(e):
            print("✅ SUCCESS: The library is installed and functional.")
            print("Internal C++ bindings are communicating with Python.")
        else:
            print(f"❌ FAILED: Unexpected Runtime Error: {e}")
            
    except ImportError as e:
        print(f"❌ FAILED: Module not found. Error: {e}")
        
    except Exception as e:
        # On Windows, if a DLL is missing, it often throws a generic Exception
        print(f"⚠️ STATUS: Library found, but returned: {e}")
        print("If it says 'Connection refused', you are 100% ready to plug in the robot.")

if __name__ == "__main__":
    check_installation()