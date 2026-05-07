# main.py - Main application file
import sys
import os
import subprocess

def check_requirements():
    # Install dependencies from requirements.txt automatically
    venv_pip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "pip.exe")
    
    if not os.path.exists(venv_pip):
        # Fallback to system pip if venv doesn't exist
        venv_pip = "pip"
        
    req_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "requirements.txt")
    if os.path.exists(req_file):
        print("Checking dependencies...")
        subprocess.run([venv_pip, "install", "-r", req_file, "-q"])

def main():
    check_requirements()
    
    # Import PyQt5 after checking requirements
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QFont
    from gui.main_window import MainWindow
    
    app = QApplication(sys.argv)
    
    # Set default font and style for the dashboard
    app.setFont(QFont("Segoe UI", 10))
    app.setStyle("Fusion")
    
    # Show main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
