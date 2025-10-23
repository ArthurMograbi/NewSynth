# testGUI_encapsulated.py
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from gui.GUIController import GUIController
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create the GUI controller
    controller = GUIController()
    
    # Initialize and show the UI
    main_window = controller.initialize_ui()
    
    # Run the application
    sys.exit(app.exec_())