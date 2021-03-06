import time
from queue import Queue

from PyQt5.QtCore import QThread, pyqtSignal

import matisse_controller.config as cfg
import matisse_controller.matisse as matisse
from matisse_controller.gui.threads import ExitFlag
from matisse_controller.gui.utils import red_text, orange_text, green_text


class StatusUpdateThread(QThread):
    """
    A QThread that periodically reads several pieces of state data and emits all of it in one HTML-formatted string.
    The interval between successive updates is specified by a configuration option.

    Some messages are colored, like for components that are at or nearing their limits.

    Note: Any Qt slots implemented in this class will be executed in the creating thread for instances of this class.
    """
    status_read = pyqtSignal(str)

    def __init__(self, matisse, messages: Queue, *args, **kwargs):
        """
        Parameters
        ----------
        matisse : matisse_controller.matisse.matisse.Matisse
        messages
            a message queue
        *args
            args to pass to `QThread.__init__`
        **kwargs
            kwargs to pass to `QThread.__init__`
        """
        super().__init__(*args, **kwargs)
        self.matisse = matisse
        self.messages = messages

    def run(self):
        while True:
            if self.messages.qsize() == 0:
                try:
                    bifi_pos = self.matisse.query('MOTBI:POS?', numeric_result=True)
                    thin_eta_pos = self.matisse.query('MOTTE:POS?', numeric_result=True)
                    refcell_pos, pz_eta_pos, slow_pz_pos = self.matisse.get_stabilizing_piezo_positions()
                    is_stabilizing = self.matisse.is_stabilizing()
                    is_scanning = self.matisse.is_scanning()
                    is_locked = self.matisse.laser_locked()
                    wavemeter_value = self.matisse.wavemeter_raw_value()

                    bifi_pos_text = f"BiFi:{bifi_pos}"
                    thin_eta_pos_text = f"Thin Eta:{thin_eta_pos}"
                    pz_eta_pos_text = f"Pz Eta:{pz_eta_pos:.3f}"
                    slow_pz_pos_text = f"Slow Pz:{slow_pz_pos:.3f}"
                    refcell_pos_text = f"RefCell:{refcell_pos:.3f}"
                    stabilizing_text = f"Stabilize:{green_text('ON') if is_stabilizing else red_text('OFF')}"
                    scanning_text = f"Scanning:{green_text('ON') if is_scanning else red_text('OFF')}"
                    locked_text = f"{green_text('LOCKED') if is_locked else red_text('NO LOCK')}"
                    wavemeter_text = f"Wavemeter:{wavemeter_value}"

                    limit_offset = cfg.get(cfg.COMPONENT_LIMIT_OFFSET)
                    refcell_at_limit = not matisse.REFERENCE_CELL_LOWER_LIMIT + limit_offset < refcell_pos < matisse.REFERENCE_CELL_UPPER_LIMIT - limit_offset
                    slow_pz_at_limit = not matisse.SLOW_PIEZO_LOWER_LIMIT + limit_offset < slow_pz_pos < matisse.SLOW_PIEZO_UPPER_LIMIT - limit_offset
                    pz_eta_at_limit = not matisse.PIEZO_ETALON_LOWER_LIMIT + limit_offset < pz_eta_pos < matisse.PIEZO_ETALON_UPPER_LIMIT - limit_offset
                    warn_offset = limit_offset * 2
                    refcell_near_limit = not matisse.REFERENCE_CELL_LOWER_LIMIT + warn_offset < refcell_pos < matisse.REFERENCE_CELL_UPPER_LIMIT - warn_offset
                    slow_pz_near_limit = not matisse.SLOW_PIEZO_LOWER_LIMIT + warn_offset < slow_pz_pos < matisse.SLOW_PIEZO_UPPER_LIMIT - warn_offset
                    pz_eta_near_limit = not matisse.PIEZO_ETALON_LOWER_LIMIT + warn_offset < pz_eta_pos < matisse.PIEZO_ETALON_UPPER_LIMIT - warn_offset

                    if refcell_at_limit:
                        refcell_pos_text = red_text(refcell_pos_text)
                    elif refcell_near_limit:
                        refcell_pos_text = orange_text(refcell_pos_text)

                    if slow_pz_at_limit:
                        slow_pz_pos_text = red_text(slow_pz_pos_text)
                    elif slow_pz_near_limit:
                        slow_pz_pos_text = orange_text(slow_pz_pos_text)

                    if pz_eta_at_limit:
                        pz_eta_pos_text = red_text(pz_eta_pos_text)
                    elif pz_eta_near_limit:
                        pz_eta_pos_text = orange_text(pz_eta_pos_text)

                    status = f"{bifi_pos_text} | {thin_eta_pos_text} | {pz_eta_pos_text} | {slow_pz_pos_text} | {refcell_pos_text} | {stabilizing_text} | {scanning_text} | {locked_text} | {wavemeter_text}"
                except Exception:
                    status = red_text('Error reading system status. Please restart if this issue persists.')
                self.status_read.emit(status)
                time.sleep(cfg.get(cfg.STATUS_MONITOR_DELAY))
            else:
                break

    def stop(self):
        self.messages.put(ExitFlag())
        self.wait()
