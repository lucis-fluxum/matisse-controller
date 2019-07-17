import os
import queue
import subprocess
import sys
import traceback

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QTextEdit, QInputDialog, QMessageBox, QApplication

from matisse import Matisse
from .handled_decorators import handled_function, handled_slot
from .logging import LoggingStream, LoggingThread, LoggingExitFlag


# TODO: Splash screen?
class ControlApplication(QApplication):
    EXIT_CODE_RESTART = 42

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_logging()
        self.setup_window()
        self.setup_menus()
        self.setup_action_listeners()
        self.setup_matisse()
        self.window.show()

    def __del__(self):
        """Tell the logging thread to gracefully exit."""
        self.log_queue.put(LoggingExitFlag())

    def setup_logging(self):
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

        # Create the queue that holds all log messages and the input stream that writes them
        self.log_queue = queue.Queue()
        self.log_stream = LoggingStream(self.log_queue)
        # Create a thread to manage receiving log messages
        self.log_thread = LoggingThread(self.log_queue, parent=self)
        self.log_thread.message_received.connect(self.log)
        self.log_thread.start()

    def setup_window(self):
        layout = QVBoxLayout()
        layout.addWidget(self.log_area)
        container = QWidget()
        container.setLayout(layout)

        self.window = window = QMainWindow()
        window.setWindowTitle('Matisse Controller')
        window.setCentralWidget(container)
        window.resize(600, 200)

    def setup_menus(self):
        menu_bar = self.window.menuBar()

        console_menu = menu_bar.addMenu('Console')
        self.clear_log_area_action = console_menu.addAction('Clear Log')
        self.open_idle_action = console_menu.addAction('Open Python Shell...')
        self.restart_action = console_menu.addAction('Restart')

        set_menu = menu_bar.addMenu('Set')
        self.set_wavelength_action = set_menu.addAction('Wavelength')
        self.set_bifi_motor_pos_action = set_menu.addAction('BiFi Motor Position')
        self.set_thin_eta_motor_pos_action = set_menu.addAction('Thin Etalon Motor Position')

        scan_menu = menu_bar.addMenu('Scan')
        self.bifi_scan_action = scan_menu.addAction('Birefringent Filter')
        self.thin_eta_scan_action = scan_menu.addAction('Thin Etalon')

        lock_menu = menu_bar.addMenu('Lock')
        self.lock_all_action = lock_menu.addAction('Lock All')
        self.lock_all_action.setCheckable(True)
        self.lock_slow_piezo_action = lock_menu.addAction('Lock Slow Piezo')
        self.lock_slow_piezo_action.setCheckable(True)
        self.lock_thin_etalon_action = lock_menu.addAction('Lock Thin Etalon')
        self.lock_thin_etalon_action.setCheckable(True)
        self.lock_piezo_etalon_action = lock_menu.addAction('Lock Piezo Etalon')
        self.lock_piezo_etalon_action.setCheckable(True)
        self.lock_fast_piezo_action = lock_menu.addAction('Lock Fast Piezo')
        self.lock_fast_piezo_action.setCheckable(True)

        tools_menu = menu_bar.addMenu('Tools')
        self.wavelength_monitor_action = tools_menu.addAction('Wavelength Monitor')

        self.lock_actions = [self.lock_slow_piezo_action, self.lock_thin_etalon_action, self.lock_piezo_etalon_action,
                             self.lock_fast_piezo_action]

    def setup_action_listeners(self):
        # Console
        self.clear_log_area_action.triggered.connect(self.clear_log_area)
        self.open_idle_action.triggered.connect(self.open_idle)
        self.restart_action.triggered.connect(self.restart)

        # Set
        self.set_wavelength_action.triggered.connect(self.set_wavelength_dialog)
        self.set_bifi_motor_pos_action.triggered.connect(self.set_bifi_motor_pos_dialog)
        self.set_thin_eta_motor_pos_action.triggered.connect(self.set_thin_eta_motor_pos_dialog)

        # Scan
        self.bifi_scan_action.triggered.connect(self.start_bifi_scan)
        self.thin_eta_scan_action.triggered.connect(self.start_thin_etalon_scan)

        # Lock
        self.lock_all_action.triggered.connect(self.toggle_lock_all)
        self.lock_slow_piezo_action.triggered.connect(self.toggle_slow_piezo_lock)
        self.lock_thin_etalon_action.triggered.connect(self.toggle_thin_etalon_lock)
        self.lock_piezo_etalon_action.triggered.connect(self.toggle_piezo_etalon_lock)
        self.lock_fast_piezo_action.triggered.connect(self.toggle_fast_piezo_lock)

        # Tools
        self.wavelength_monitor_action.triggered.connect(self.start_wavelength_monitor)

    @handled_function
    def setup_matisse(self):
        # TODO: Initialize Matisse
        self.matisse: Matisse = None

    @pyqtSlot(str)
    def log(self, message):
        self.log_area.moveCursor(QTextCursor.End)
        self.log_area.insertPlainText(message)

    def error_dialog(self):
        stack = list(traceback.format_exception(*sys.exc_info()))
        # Pick length of longest line in stack, with a cutoff at 185
        desired_width = min(max([len(line) for line in stack]), 185)
        description = stack.pop()
        print(description, end='')
        # Remove entries for handled_function decorator, for clarity
        stack = filter(lambda item: os.path.join('gui', 'handled_decorators.py') not in item, stack)
        dialog = QMessageBox(icon=QMessageBox.Critical)
        dialog.setWindowTitle('Error')
        # Adding the underscores is a hack to resize the QMessageBox because it's not normally resizable.
        # This looks good in Windows, haven't tested other platforms. Sorry :(
        dialog.setText(f"{description + '_' * desired_width}\n\n{''.join(stack)}")
        dialog.exec()

    @handled_slot(bool)
    def clear_log_area(self, checked):
        self.log_area.clear()

    @handled_slot(bool)
    def open_idle(self, checked):
        print('Opening IDLE.')
        subprocess.Popen('python -m idlelib -t "Matisse Controller - Python Shell" -c "from matisse import Matisse; ' +
                         'matisse = Matisse(); print(\'Access the Matisse using \\\'matisse.[method]\\\'\')"')

    @handled_slot(bool)
    def restart(self, checked):
        self.exit(self.EXIT_CODE_RESTART)

    @handled_slot(bool)
    def set_wavelength_dialog(self, checked):
        # TODO: Set default value to current target wavelength or just to the middle
        target_wavelength, success = QInputDialog.getDouble(self.window, 'Set Wavelength', 'Wavelength (nm): ')
        if success:
            print(f"Setting wavelength to {target_wavelength} nm...")
            self.matisse.set_wavelength(target_wavelength)

    @handled_slot(bool)
    def set_bifi_motor_pos_dialog(self, checked):
        # TODO: Set default value to current position or just to the middle
        target_pos, success = QInputDialog.getInt(self.window, 'Set BiFi Motor Position', 'Absolute Position:')
        if success:
            print(f"Setting BiFi motor position to {target_pos}.")
            self.matisse.set_bifi_motor_pos(target_pos)

    @handled_slot(bool)
    def set_thin_eta_motor_pos_dialog(self, checked):
        # TODO: Set default value to current position or just to the middle
        target_pos, success = QInputDialog.getInt(self.window, 'Set Thin Etalon Motor Position', 'Absolute Position:')
        if success:
            print(f"Setting thin etalon motor position to {target_pos}.")
            self.matisse.set_thin_etalon_motor_pos(target_pos)

    @handled_slot(bool)
    def start_bifi_scan(self, checked):
        print('Starting BiFi scan...')
        self.matisse.birefringent_filter_scan()

    @handled_slot(bool)
    def start_thin_etalon_scan(self, checked):
        print('Starting thin etalon scan...')
        self.matisse.thin_etalon_scan()

    @handled_slot(bool)
    def toggle_lock_all(self, checked):
        if checked:
            for action in self.lock_actions:
                if not action.isChecked():
                    action.trigger()
            if all([action.isChecked() for action in self.lock_actions]):
                [action.setEnabled(False) for action in self.lock_actions]
            else:
                self.lock_all_action.setChecked(False)
                print("Couldn't lock all laser components.")
        else:
            for action in reversed(self.lock_actions):
                action.trigger()
                action.setEnabled(True)

    @handled_slot(bool)
    def toggle_slow_piezo_lock(self, checked):
        print(f"{'Locking' if checked else 'Unlocking'} slow piezo.")
        self.lock_slow_piezo_action.setChecked(not checked)
        self.matisse.set_slow_piezo_lock(checked)
        self.lock_slow_piezo_action.setChecked(checked)

    @handled_slot(bool)
    def toggle_thin_etalon_lock(self, checked):
        print(f"{'Locking' if checked else 'Unlocking'} thin etalon.")
        self.lock_thin_etalon_action.setChecked(not checked)
        self.matisse.set_thin_etalon_lock(checked)
        self.lock_thin_etalon_action.setChecked(checked)

    @handled_slot(bool)
    def toggle_piezo_etalon_lock(self, checked):
        print(f"{'Locking' if checked else 'Unlocking'} piezo etalon.")
        self.lock_piezo_etalon_action.setChecked(not checked)
        self.matisse.set_piezo_etalon_lock(checked)
        self.lock_piezo_etalon_action.setChecked(checked)

    @handled_slot(bool)
    def toggle_fast_piezo_lock(self, checked):
        print(f"{'Locking' if checked else 'Unlocking'} fast piezo.")
        self.lock_fast_piezo_action.setChecked(not checked)
        self.matisse.set_piezo_etalon_lock(checked)
        self.lock_fast_piezo_action.setChecked(checked)

    @handled_slot(bool)
    def start_wavelength_monitor(self, checked):
        print('Starting wavelength monitor.')
        raise NotImplementedError
