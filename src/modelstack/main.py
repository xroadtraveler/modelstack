# [10000] Beacon intent: Application entry point

import sys
from PyQt6.QtWidgets import QApplication

from modelstack.gui.main_window import MainWindow


# [010] Module intent: launch ModelStack PyQt6 application

def main() -> None:

    # [001] initialize Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("ModelStack")
    # [-----END [001]-----]

    # [002] create and show main window
    window = MainWindow()
    window.show()
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