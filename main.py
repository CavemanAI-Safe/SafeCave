import sys
import os
import json
from PySide6.QtWidgets import QApplication
from CaveSetup import CaveSetupWizard, SettingsManager # Assuming you saved the previous code as CaveSetup.py
from SafeCave_Pro import SafeCaveMothership, SafeCaveController # Your main surveillance script

def run_caveman_ai():
    app = QApplication(sys.argv)
    settings_mgr = SettingsManager()
    
    # 1. Check if the "Cave" is already configured
    if not os.path.exists("cave_config.json"):
        print("CavemanAI LOG: Initial Setup Required.")
        wizard = CaveSetupWizard()
        wizard.show()
        # We use a nested event loop or wait for the wizard to close
        app.exec() 
        
        # After wizard closes, re-check if file was actually created
        if not os.path.exists("cave_config.json"):
            print("Setup cancelled. Exiting.")
            return

    # 2. Launch the Mothership with the saved configuration
    config = settings_mgr.load()
    saved_ips = config.get("ips", [])
    
    # Initialize the Surveillance Grid
    monitor = SafeCaveMothership(saved_ips) # Note: We update Mothership to accept IPs
    monitor.show()
    
    # Initialize the Independent Hub
    controller = SafeCaveController(monitor.units)
    controller.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_caveman_ai()
