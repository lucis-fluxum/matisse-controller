from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import *

import matisse_controller.config as cfg
from matisse_controller.matisse import Matisse


class ConfigurationDialog(QDialog):
    """A dialog for displaying and modifying selected configurable options that affect the behavior of the program."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('Configuration')
        self.resize(700, 200)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.add_options()
        self.set_current_values_from_config()
        self.add_buttons()

    # TODO: Tooltips
    def add_options(self):
        general_options = self.create_general_options()
        scan_options = self.create_scan_options()
        locking_options = self.create_locking_options()

        form = QWidget()
        form_layout = QHBoxLayout()
        form.setLayout(form_layout)
        col_1 = QVBoxLayout()
        col_1.addWidget(general_options)
        col_1.addWidget(scan_options)
        form_layout.addLayout(col_1)
        form_layout.addWidget(locking_options)
        self.layout.addWidget(form)

    def create_general_options(self):
        general_options = QGroupBox('General')
        general_layout = QFormLayout()
        general_options.setLayout(general_layout)
        self.matisse_device_id_field = QLineEdit()
        general_layout.addRow('Matisse device ID: ', self.matisse_device_id_field)
        self.wavelength_lower_limit_field = QDoubleSpinBox()
        self.wavelength_lower_limit_field.setMinimum(0)
        self.wavelength_lower_limit_field.setMaximum(2000)
        self.wavemeter_port_field = QLineEdit()
        general_layout.addRow('Wavemeter port: ', self.wavemeter_port_field)
        self.wavemeter_precision_field = QSpinBox()
        self.wavemeter_precision_field.setMinimum(0)
        general_layout.addRow('Wavemeter precision: ', self.wavemeter_precision_field)
        general_layout.addRow('Wavelength lower limit: ', self.wavelength_lower_limit_field)
        self.wavelength_upper_limit_field = QDoubleSpinBox()
        self.wavelength_upper_limit_field.setMinimum(0)
        self.wavelength_upper_limit_field.setMaximum(2000)
        general_layout.addRow('Wavelength upper limit: ', self.wavelength_upper_limit_field)
        return general_options

    def create_scan_options(self):
        scan_options = QGroupBox('Scanning')
        scan_layout = QFormLayout()
        scan_options.setLayout(scan_layout)
        self.bifi_scan_range_field = QSpinBox()
        self.bifi_scan_range_field.setMaximum(Matisse.BIREFRINGENT_FILTER_UPPER_LIMIT / 2)
        scan_layout.addRow('BiFi normal scan range:', self.bifi_scan_range_field)
        self.bifi_small_scan_range_field = QSpinBox()
        self.bifi_small_scan_range_field.setMaximum(Matisse.BIREFRINGENT_FILTER_UPPER_LIMIT / 4)
        scan_layout.addRow('BiFi small scan range:', self.bifi_small_scan_range_field)
        self.bifi_scan_step_field = QSpinBox()
        scan_layout.addRow('BiFi scan step:', self.bifi_scan_step_field)
        self.thin_eta_scan_range_field = QSpinBox()
        self.thin_eta_scan_range_field.setMaximum(Matisse.THIN_ETALON_UPPER_LIMIT / 2)
        scan_layout.addRow('Thin etalon normal scan range:', self.thin_eta_scan_range_field)
        self.thin_eta_small_scan_range_field = QSpinBox()
        self.thin_eta_small_scan_range_field.setMaximum(Matisse.THIN_ETALON_UPPER_LIMIT / 4)
        scan_layout.addRow('Thin etalon small scan range:', self.thin_eta_small_scan_range_field)
        self.thin_eta_scan_step_field = QSpinBox()
        scan_layout.addRow('Thin etalon scan step:', self.thin_eta_scan_step_field)
        self.thin_eta_nudge_field = QSpinBox()
        scan_layout.addRow('Thin etalon scan nudge:', self.thin_eta_nudge_field)
        self.refcell_rising_speed_field = QDoubleSpinBox()
        self.refcell_rising_speed_field.setDecimals(3)
        self.refcell_rising_speed_field.setSingleStep(0.001)
        self.refcell_rising_speed_field.setMinimum(0)
        self.refcell_rising_speed_field.setMaximum(0.1)
        scan_layout.addRow('RefCell scan rising speed: ', self.refcell_rising_speed_field)
        self.refcell_falling_speed_field = QDoubleSpinBox()
        self.refcell_falling_speed_field.setDecimals(3)
        self.refcell_falling_speed_field.setSingleStep(0.001)
        self.refcell_falling_speed_field.setMinimum(0)
        self.refcell_falling_speed_field.setMaximum(0.1)
        scan_layout.addRow('RefCell scan falling speed: ', self.refcell_falling_speed_field)
        self.large_wavelength_drift_field = QDoubleSpinBox()
        scan_layout.addRow('Large wavelength drift: ', self.large_wavelength_drift_field)
        self.medium_wavelength_drift_field = QDoubleSpinBox()
        scan_layout.addRow('Medium wavelength drift: ', self.medium_wavelength_drift_field)
        self.small_wavelength_drift_field = QDoubleSpinBox()
        scan_layout.addRow('Small wavelength drift: ', self.small_wavelength_drift_field)
        return scan_options

    def create_locking_options(self):
        locking_options = QGroupBox('Locking/Stabilization')
        locking_layout = QFormLayout()
        locking_options.setLayout(locking_layout)
        self.locking_timeout_field = QDoubleSpinBox()
        self.locking_timeout_field.setMinimum(0)
        locking_layout.addRow('Locking timeout: ', self.locking_timeout_field)
        self.pz_eta_upper_correction_pos_field = QDoubleSpinBox()
        self.pz_eta_upper_correction_pos_field.setSingleStep(0.01)
        self.pz_eta_upper_correction_pos_field.setMinimum(Matisse.PIEZO_ETALON_LOWER_LIMIT)
        self.pz_eta_upper_correction_pos_field.setMaximum(Matisse.PIEZO_ETALON_UPPER_LIMIT)
        locking_layout.addRow('Piezo etalon upper correction pos: ', self.pz_eta_upper_correction_pos_field)
        self.slow_pz_upper_correction_pos_field = QDoubleSpinBox()
        self.slow_pz_upper_correction_pos_field.setSingleStep(0.01)
        self.slow_pz_upper_correction_pos_field.setMinimum(Matisse.SLOW_PIEZO_LOWER_LIMIT)
        self.slow_pz_upper_correction_pos_field.setMaximum(Matisse.SLOW_PIEZO_UPPER_LIMIT)
        locking_layout.addRow('Slow piezo upper correction pos: ', self.slow_pz_upper_correction_pos_field)
        self.refcell_upper_correction_pos_field = QDoubleSpinBox()
        self.refcell_upper_correction_pos_field.setSingleStep(0.01)
        self.refcell_upper_correction_pos_field.setMinimum(Matisse.REFERENCE_CELL_LOWER_LIMIT)
        self.refcell_upper_correction_pos_field.setMaximum(Matisse.REFERENCE_CELL_UPPER_LIMIT)
        locking_layout.addRow('RefCell upper correction pos: ', self.refcell_upper_correction_pos_field)
        self.pz_eta_mid_correction_pos_field = QDoubleSpinBox()
        self.pz_eta_mid_correction_pos_field.setSingleStep(0.01)
        self.pz_eta_mid_correction_pos_field.setMinimum(Matisse.PIEZO_ETALON_LOWER_LIMIT)
        self.pz_eta_mid_correction_pos_field.setMaximum(Matisse.PIEZO_ETALON_UPPER_LIMIT)
        locking_layout.addRow('Piezo etalon mid correction pos: ', self.pz_eta_mid_correction_pos_field)
        self.slow_pz_mid_correction_pos_field = QDoubleSpinBox()
        self.slow_pz_mid_correction_pos_field.setSingleStep(0.01)
        self.slow_pz_mid_correction_pos_field.setMinimum(Matisse.SLOW_PIEZO_LOWER_LIMIT)
        self.slow_pz_mid_correction_pos_field.setMaximum(Matisse.SLOW_PIEZO_UPPER_LIMIT)
        locking_layout.addRow('Slow piezo mid correction pos: ', self.slow_pz_mid_correction_pos_field)
        self.refcell_mid_correction_pos_field = QDoubleSpinBox()
        self.refcell_mid_correction_pos_field.setSingleStep(0.01)
        self.refcell_mid_correction_pos_field.setMinimum(Matisse.REFERENCE_CELL_LOWER_LIMIT)
        self.refcell_mid_correction_pos_field.setMaximum(Matisse.REFERENCE_CELL_UPPER_LIMIT)
        locking_layout.addRow('RefCell mid correction pos: ', self.refcell_mid_correction_pos_field)
        self.pz_eta_lower_correction_pos_field = QDoubleSpinBox()
        self.pz_eta_lower_correction_pos_field.setSingleStep(0.01)
        self.pz_eta_lower_correction_pos_field.setMinimum(Matisse.PIEZO_ETALON_LOWER_LIMIT)
        self.pz_eta_lower_correction_pos_field.setMaximum(Matisse.PIEZO_ETALON_UPPER_LIMIT)
        locking_layout.addRow('Piezo etalon lower correction pos: ', self.pz_eta_lower_correction_pos_field)
        self.slow_pz_lower_correction_pos_field = QDoubleSpinBox()
        self.slow_pz_lower_correction_pos_field.setSingleStep(0.01)
        self.slow_pz_lower_correction_pos_field.setMinimum(Matisse.SLOW_PIEZO_LOWER_LIMIT)
        self.slow_pz_lower_correction_pos_field.setMaximum(Matisse.SLOW_PIEZO_UPPER_LIMIT)
        locking_layout.addRow('Slow piezo lower correction pos: ', self.slow_pz_lower_correction_pos_field)
        self.refcell_lower_correction_pos_field = QDoubleSpinBox()
        self.refcell_lower_correction_pos_field.setSingleStep(0.01)
        self.refcell_lower_correction_pos_field.setMinimum(Matisse.REFERENCE_CELL_LOWER_LIMIT)
        self.refcell_lower_correction_pos_field.setMaximum(Matisse.REFERENCE_CELL_UPPER_LIMIT)
        locking_layout.addRow('RefCell lower correction pos: ', self.refcell_lower_correction_pos_field)
        self.stabilization_rising_speed_field = QDoubleSpinBox()
        self.stabilization_rising_speed_field.setDecimals(3)
        self.stabilization_rising_speed_field.setSingleStep(0.001)
        self.stabilization_rising_speed_field.setMinimum(0)
        self.stabilization_rising_speed_field.setMaximum(0.1)
        locking_layout.addRow('Auto-stabilization rising speed: ', self.stabilization_rising_speed_field)
        self.stabilization_falling_speed_field = QDoubleSpinBox()
        self.stabilization_falling_speed_field.setDecimals(3)
        self.stabilization_falling_speed_field.setSingleStep(0.001)
        self.stabilization_falling_speed_field.setMinimum(0)
        self.stabilization_falling_speed_field.setMaximum(0.1)
        locking_layout.addRow('Auto-stabilization falling speed: ', self.stabilization_falling_speed_field)
        self.stabilization_delay_field = QDoubleSpinBox()
        self.stabilization_delay_field.setMinimum(0.1)
        locking_layout.addRow('Auto-stabilization delay: ', self.stabilization_delay_field)
        self.stabilization_tolerance_field = QDoubleSpinBox()
        self.stabilization_tolerance_field.setDecimals(4)
        self.stabilization_tolerance_field.setSingleStep(0.0001)
        self.stabilization_tolerance_field.setMinimum(0.0001)
        locking_layout.addRow('Auto-stabilization tolerance: ', self.stabilization_tolerance_field)
        return locking_options

    def set_current_values_from_config(self):
        self.matisse_device_id_field.setText(cfg.get(cfg.MATISSE_DEVICE_ID))
        self.wavemeter_port_field.setText(cfg.get(cfg.WAVEMETER_PORT))
        self.wavemeter_precision_field.setValue(cfg.get(cfg.WAVEMETER_PRECISION))
        self.wavelength_lower_limit_field.setValue(cfg.get(cfg.WAVELENGTH_LOWER_LIMIT))
        self.wavelength_upper_limit_field.setValue(cfg.get(cfg.WAVELENGTH_UPPER_LIMIT))

        self.bifi_scan_range_field.setValue(cfg.get(cfg.BIFI_SCAN_RANGE))
        self.bifi_small_scan_range_field.setValue(cfg.get(cfg.BIFI_SCAN_RANGE_SMALL))
        self.bifi_scan_step_field.setValue(cfg.get(cfg.BIFI_SCAN_STEP))

        self.thin_eta_scan_range_field.setValue(cfg.get(cfg.THIN_ETA_SCAN_RANGE))
        self.thin_eta_small_scan_range_field.setValue(cfg.get(cfg.THIN_ETA_SCAN_RANGE_SMALL))
        self.thin_eta_scan_step_field.setValue(cfg.get(cfg.THIN_ETA_SCAN_STEP))
        self.thin_eta_nudge_field.setValue(cfg.get(cfg.THIN_ETA_NUDGE))

        self.refcell_rising_speed_field.setValue(cfg.get(cfg.REFCELL_SCAN_RISING_SPEED))
        self.refcell_falling_speed_field.setValue(cfg.get(cfg.REFCELL_SCAN_FALLING_SPEED))

        self.large_wavelength_drift_field.setValue(cfg.get(cfg.LARGE_WAVELENGTH_DRIFT))
        self.medium_wavelength_drift_field.setValue(cfg.get(cfg.MEDIUM_WAVELENGTH_DRIFT))
        self.small_wavelength_drift_field.setValue(cfg.get(cfg.SMALL_WAVELENGTH_DRIFT))

        self.locking_timeout_field.setValue(cfg.get(cfg.LOCKING_TIMEOUT))

        self.pz_eta_upper_correction_pos_field.setValue(cfg.get(cfg.PIEZO_ETA_UPPER_CORRECTION_POS))
        self.slow_pz_upper_correction_pos_field.setValue(cfg.get(cfg.SLOW_PIEZO_UPPER_CORRECTION_POS))
        self.refcell_upper_correction_pos_field.setValue(cfg.get(cfg.REFCELL_UPPER_CORRECTION_POS))
        self.pz_eta_mid_correction_pos_field.setValue(cfg.get(cfg.PIEZO_ETA_MID_CORRECTION_POS))
        self.slow_pz_mid_correction_pos_field.setValue(cfg.get(cfg.SLOW_PIEZO_MID_CORRECTION_POS))
        self.refcell_mid_correction_pos_field.setValue(cfg.get(cfg.REFCELL_MID_CORRECTION_POS))
        self.pz_eta_lower_correction_pos_field.setValue(cfg.get(cfg.PIEZO_ETA_LOWER_CORRECTION_POS))
        self.slow_pz_lower_correction_pos_field.setValue(cfg.get(cfg.SLOW_PIEZO_LOWER_CORRECTION_POS))
        self.refcell_lower_correction_pos_field.setValue(cfg.get(cfg.REFCELL_LOWER_CORRECTION_POS))

        self.stabilization_rising_speed_field.setValue(cfg.get(cfg.STABILIZATION_RISING_SPEED))
        self.stabilization_falling_speed_field.setValue(cfg.get(cfg.STABILIZATION_FALLING_SPEED))
        self.stabilization_delay_field.setValue(cfg.get(cfg.STABILIZATION_DELAY))
        self.stabilization_tolerance_field.setValue(cfg.get(cfg.STABILIZATION_TOLERANCE))

    def add_buttons(self):
        button_box = QDialogButtonBox(QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save |
                                      QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.RestoreDefaults).clicked.connect(self.restore_defaults)
        button_box.button(QDialogButtonBox.Save).clicked.connect(self.save_configuration)
        button_box.button(QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.layout.addWidget(button_box)

    @pyqtSlot(bool)
    def restore_defaults(self, checked):
        cfg.restore_defaults()
        self.set_current_values_from_config()

    @pyqtSlot(bool)
    def save_configuration(self, checked):
        print('Saving configuration.')
        cfg.set(cfg.MATISSE_DEVICE_ID, self.matisse_device_id_field.text())
        cfg.set(cfg.WAVEMETER_PORT, self.wavemeter_port_field.text())
        cfg.set(cfg.WAVEMETER_PRECISION, self.wavemeter_precision_field.value())
        cfg.set(cfg.WAVELENGTH_LOWER_LIMIT, self.wavelength_lower_limit_field.value())
        cfg.set(cfg.WAVELENGTH_UPPER_LIMIT, self.wavelength_upper_limit_field.value())

        cfg.set(cfg.BIFI_SCAN_RANGE, self.bifi_scan_range_field.value())
        cfg.set(cfg.BIFI_SCAN_RANGE_SMALL, self.bifi_small_scan_range_field.value())
        cfg.set(cfg.BIFI_SCAN_STEP, self.bifi_scan_step_field.value())

        cfg.set(cfg.THIN_ETA_SCAN_RANGE, self.thin_eta_scan_range_field.value())
        cfg.set(cfg.THIN_ETA_SCAN_RANGE_SMALL, self.thin_eta_small_scan_range_field.value())
        cfg.set(cfg.THIN_ETA_SCAN_STEP, self.thin_eta_scan_step_field.value())
        cfg.set(cfg.THIN_ETA_NUDGE, self.thin_eta_nudge_field.value())

        cfg.set(cfg.REFCELL_SCAN_RISING_SPEED, self.refcell_rising_speed_field.value())
        cfg.set(cfg.REFCELL_SCAN_FALLING_SPEED, self.refcell_falling_speed_field.value())

        cfg.set(cfg.LARGE_WAVELENGTH_DRIFT, self.large_wavelength_drift_field.value())
        cfg.set(cfg.MEDIUM_WAVELENGTH_DRIFT, self.medium_wavelength_drift_field.value())
        cfg.set(cfg.SMALL_WAVELENGTH_DRIFT, self.small_wavelength_drift_field.value())

        cfg.set(cfg.LOCKING_TIMEOUT, self.locking_timeout_field.value())

        cfg.set(cfg.PIEZO_ETA_UPPER_CORRECTION_POS, self.pz_eta_upper_correction_pos_field.value())
        cfg.set(cfg.SLOW_PIEZO_UPPER_CORRECTION_POS, self.slow_pz_upper_correction_pos_field.value())
        cfg.set(cfg.REFCELL_UPPER_CORRECTION_POS, self.refcell_upper_correction_pos_field.value())
        cfg.set(cfg.PIEZO_ETA_MID_CORRECTION_POS, self.pz_eta_mid_correction_pos_field.value())
        cfg.set(cfg.SLOW_PIEZO_MID_CORRECTION_POS, self.slow_pz_mid_correction_pos_field.value())
        cfg.set(cfg.REFCELL_MID_CORRECTION_POS, self.refcell_mid_correction_pos_field.value())
        cfg.set(cfg.PIEZO_ETA_LOWER_CORRECTION_POS, self.pz_eta_lower_correction_pos_field.value())
        cfg.set(cfg.SLOW_PIEZO_LOWER_CORRECTION_POS, self.slow_pz_lower_correction_pos_field.value())
        cfg.set(cfg.REFCELL_LOWER_CORRECTION_POS, self.refcell_lower_correction_pos_field.value())

        cfg.set(cfg.STABILIZATION_RISING_SPEED, self.stabilization_rising_speed_field.value())
        cfg.set(cfg.STABILIZATION_FALLING_SPEED, self.stabilization_falling_speed_field.value())
        cfg.set(cfg.STABILIZATION_DELAY, self.stabilization_delay_field.value())
        cfg.set(cfg.STABILIZATION_TOLERANCE, self.stabilization_tolerance_field.value())

        # TODO: GUI config
        # cfg.set('gui', {})

        cfg.save()
        self.close()

    @pyqtSlot(bool)
    def cancel(self, checked):
        self.close()


def main():
    app = QApplication([])
    d = ConfigurationDialog()
    d.exec()
    app.exit()


if __name__ == '__main__':
    main()