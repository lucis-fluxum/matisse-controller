import sys
from traceback import format_exception

from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QWidget, QTextEdit, QMessageBox

from .handled_slot import HandledSlot


class Gui(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_menus()
        self.lock_actions = [self.lock_slow_piezo_action, self.lock_thin_etalon_action, self.lock_piezo_etalon_action,
                             self.lock_fast_piezo_action]

        self.log_area = log_area = QTextEdit()
        log_area.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(log_area)

        container = QWidget()
        container.setLayout(layout)
        self.setWindowTitle('Matisse Controller')
        self.setCentralWidget(container)
        self.resize(600, 200)
        self.show()

    def setup_menus(self):
        menu_bar = self.menuBar()

        console_menu = menu_bar.addMenu('Console')
        self.clear_console_action = console_menu.addAction('Clear Log')
        self.clear_console_action.triggered.connect(lambda: self.log_area.clear())
        self.open_shell_action = console_menu.addAction('Open Python Shell...')
        self.open_shell_action.triggered.connect(lambda: self.log('Launching Python shell.'))
        # TODO: Open python shell with access to any relevant objects

        set_menu = menu_bar.addMenu('Set')
        self.set_wavelength_action = set_menu.addAction('Wavelength')
        self.set_bifi_motor_pos_action = set_menu.addAction('BiFi Motor Position')
        self.set_thin_eta_motor_pos_action = set_menu.addAction('Thin Etalon Motor Position')

        scan_menu = menu_bar.addMenu('Scan')
        self.bifi_scan_action = scan_menu.addAction('Birefringent Filter')
        self.thin_eta_scan_action = scan_menu.addAction('Thin Etalon')

        lock_menu = menu_bar.addMenu('Lock')
        self.lock_all_action = lock_all_action = lock_menu.addAction('Lock All')
        lock_all_action.setCheckable(True)
        lock_all_action.toggled.connect(self.lock_all)
        self.lock_slow_piezo_action = lock_slow_piezo_action = lock_menu.addAction('Lock Slow Piezo')
        lock_slow_piezo_action.setCheckable(True)
        lock_slow_piezo_action.toggled.connect(self.toggle_slow_piezo_lock)
        self.lock_thin_etalon_action = lock_thin_etalon_action = lock_menu.addAction('Lock Thin Etalon')
        lock_thin_etalon_action.setCheckable(True)
        lock_thin_etalon_action.toggled.connect(self.toggle_thin_etalon_lock)
        self.lock_piezo_etalon_action = lock_piezo_etalon_action = lock_menu.addAction('Lock Piezo Etalon')
        lock_piezo_etalon_action.setCheckable(True)
        lock_piezo_etalon_action.toggled.connect(self.toggle_piezo_etalon_lock)
        self.lock_fast_piezo_action = lock_fast_piezo_action = lock_menu.addAction('Lock Fast Piezo')
        lock_fast_piezo_action.setCheckable(True)
        lock_fast_piezo_action.toggled.connect(self.toggle_fast_piezo_lock)

    def log(self, message, end='\n'):
        self.log_area.setText(self.log_area.toPlainText() + message + end)

    def error_dialog(self):
        stack = format_exception(*sys.exc_info())
        stack.pop(1)  # Remove entry for the HandledSlot decorator, for clarity
        description = stack.pop()  # Grab exception message to use as the description
        msg_box = QMessageBox(icon=QMessageBox.Critical, text=f"{description}\n{''.join(stack)}")
        msg_box.setWindowTitle('Error')
        msg_box.exec()

    @HandledSlot('bool')
    def lock_all(self, lock):
        if lock:
            for action in self.lock_actions:
                action.setChecked(True)
                action.setEnabled(False)
        else:
            for action in reversed(self.lock_actions):
                action.setChecked(False)
                action.setEnabled(True)

    @HandledSlot('bool')
    def toggle_slow_piezo_lock(self, lock):
        self.log(f"{'Locking' if lock else 'Unlocking'} slow piezo... ", end='')
        raise NotImplementedError
        self.log('Done.')

    @HandledSlot('bool')
    def toggle_thin_etalon_lock(self, lock):
        self.log(f"{'Locking' if lock else 'Unlocking'} thin etalon... ", end='')
        raise NotImplementedError
        self.log('Done.')

    @HandledSlot('bool')
    def toggle_piezo_etalon_lock(self, lock):
        self.log(f"{'Locking' if lock else 'Unlocking'} piezo etalon... ", end='')
        raise NotImplementedError
        self.log('Done.')

    @HandledSlot('bool')
    def toggle_fast_piezo_lock(self, lock):
        self.log(f"{'Locking' if lock else 'Unlocking'} fast piezo... ", end='')
        raise NotImplementedError
        self.log('Done.')
