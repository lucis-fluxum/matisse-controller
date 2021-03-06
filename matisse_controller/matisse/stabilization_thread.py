import threading
import time
from queue import Queue

import matisse_controller.config as cfg
import matisse_controller.matisse as matisse
from matisse_controller.matisse.event_report import log_event, EventType


class StabilizationThread(threading.Thread):
    def __init__(self, matisse, messages: Queue, *args, **kwargs):
        """
        Parameters
        ----------
        matisse : matisse_controller.matisse.matisse.Matisse
        messages
            a message queue
        *args
            args to pass to `Thread.__init__`
        **kwargs
            kwargs to pass to `Thread.__init__`
        """
        super().__init__(*args, **kwargs)
        self._matisse = matisse
        self.messages = messages
        # Stop any running scans just in case
        self._matisse.stop_scan()
        self._matisse.query(f"SCAN:RISINGSPEED {cfg.get(cfg.STABILIZATION_RISING_SPEED)}")
        self._matisse.query(f"SCAN:FALLINGSPEED {cfg.get(cfg.STABILIZATION_FALLING_SPEED)}")

    def run(self):
        """
        Try to keep the measured wavelength within the configured tolerance by scanning the reference cell.

        If a larger drift in wavelength occurs, we might have fallen into a dip on the power diode curve. To correct
        this, a small BiFi scan and a small thin etalon scan will be performed.

        Exit if anything is pushed to the message queue.
        """
        while True:
            if self.messages.qsize() == 0:
                current_wavelength = self._matisse.wavemeter_wavelength()
                drift = round(current_wavelength - self._matisse.target_wavelength, cfg.get(cfg.WAVEMETER_PRECISION))
                # TODO: This threshold is large, maybe add another config option for this condition
                if abs(drift) > cfg.get(cfg.LARGE_WAVELENGTH_DRIFT):
                    # TODO: Consider logging this event to the event report
                    print(f"WARNING: Wavelength drifted by {drift} nm during stabilization. Making corrections.")
                    self._matisse.stop_scan()
                    if self._matisse.is_lock_correction_on():
                        self._matisse.stop_laser_lock_correction()
                    # TODO: Skip BiFi scan if drift is small enough, kind of like in Matisse.set_wavelength
                    self._matisse.birefringent_filter_scan(scan_range=cfg.get(cfg.BIFI_SCAN_RANGE_SMALL))
                    self._matisse.thin_etalon_scan(scan_range=cfg.get(cfg.THIN_ETA_SCAN_RANGE_SMALL))
                    self._matisse.start_laser_lock_correction()
                elif abs(drift) > cfg.get(cfg.STABILIZATION_TOLERANCE):
                    if drift > 0:
                        # measured wavelength is too high
                        print(f"Wavelength too high, decreasing. Drift is {drift} nm. Refcell is at {self._matisse.query('SCAN:NOW?', numeric_result=True)}")
                        if not self._matisse.is_any_limit_reached():
                            if cfg.get(cfg.REPORT_EVENTS):
                                log_event(EventType.WAVELENGTH_DRIFT, self._matisse, current_wavelength,
                                          f"wavelength drifted by {drift} nm")
                            self._matisse.start_scan(matisse.SCAN_MODE_DOWN)
                        else:
                            self.do_stabilization_correction(current_wavelength)
                    else:
                        # measured wavelength is too low
                        print(f"Wavelength too low, increasing.  Drift is {drift} nm. Refcell is at {self._matisse.query('SCAN:NOW?', numeric_result=True)}")
                        if not self._matisse.is_any_limit_reached():
                            if cfg.get(cfg.REPORT_EVENTS):
                                log_event(EventType.WAVELENGTH_DRIFT, self._matisse, current_wavelength,
                                          f"wavelength drifted by {drift} nm")
                            self._matisse.start_scan(matisse.SCAN_MODE_UP)
                        else:
                            self.do_stabilization_correction(current_wavelength)
                else:
                    self._matisse.stop_scan()
                    # print(f"Within tolerance. Drift is {drift}")
                time.sleep(cfg.get(cfg.STABILIZATION_DELAY))
            else:
                self._matisse.stop_scan()
                break

    def do_stabilization_correction(self, wavelength):
        """Reset the stabilization piezos and optionally log the correction event."""
        print('WARNING: A component has hit a limit while adjusting the RefCell. Attempting automatic corrections.')
        self._matisse.stop_scan()
        if cfg.get(cfg.REPORT_EVENTS):
            log_event(EventType.STABILIZATION_CORRECTION, self._matisse, wavelength,
                      'component hit a limit while auto-stabilization was on')
        self._matisse.reset_stabilization_piezos()
        self._matisse.stabilization_auto_corrections += 1
