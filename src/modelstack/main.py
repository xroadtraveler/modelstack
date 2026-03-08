# [10000] Beacon intent: Application entry point

# [010] Module intent: launch ModelStack PyQt6 application

def main() -> None:

    # [001] initialize Qt application
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("ModelStack")
    # [-----END [001]-----]

    # [002] create and show main window
    # TODO: from gui.main_window import MainWindow
    # TODO: window = MainWindow()
    # TODO: window.show()
    # [-----END [002]-----]

    # [003] execute event loop
    sys.exit(app.exec())
    # [-----END [003]-----]

# [-----END [010]-----]


# [20000] Beacon intent: Script entry guard

# [010] enforce script entry

if __name__ == "__main__":
    main()
# [-----END [010]-----]