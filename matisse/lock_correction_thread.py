import threading
import time
from queue import Queue

from matisse.control_loops_on import ControlLoopsOn


class LockCorrectionThread(threading.Thread):
    """
    Runs while the fast piezo attempts to obtain a lock. Exits if the laser cannot lock within a certain timeout, or if
    a component reaches its limit while trying to lock. If the laser locks within the timeout, but a component has
    reached its limit, makes an automatic correction to the slow piezo, piezo etalon, and RefCell.

    TODO: Set recommended setpoint for fast piezo
    """

    UNABLE_TO_LOCK_MESSAGE = 'Try manually stabilizing the laser output power. Alternatively, try setting the ' \
                             'recommended fast piezo setpoint. '

    def __init__(self, matisse, timeout: float, messages: Queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.matisse = matisse
        self.messages = messages
        self.timeout = timeout
        self.timer = threading.Timer(self.timeout, self.quit_unless_locked)

    def run(self):
        # TODO: Only reset piezos that are too far towards their limits
        self.matisse.reset_stabilization_piezos()
        with ControlLoopsOn(self.matisse):
            self.timer.start()
            while True:
                if self.messages.qsize() == 0:
                    if self.matisse.fast_piezo_locked():
                        self.timer.cancel()
                        if self.matisse.is_any_limit_reached():
                            print('WARNING: A component has hit a limit while the laser is locked. '
                                  'Attempting automatic corrections.')
                            self.matisse.reset_stabilization_piezos()
                    else:
                        self.restart_timer()
                        if self.matisse.is_any_limit_reached():
                            print('WARNING: A component has hit a limit before the laser could lock. '
                                  'Stopping control loops. ', LockCorrectionThread.UNABLE_TO_LOCK_MESSAGE)
                            self.timer.cancel()
                            break

                    time.sleep(1)
                else:
                    self.timer.cancel()
                    break

    def quit_unless_locked(self):
        if not self.matisse.fast_piezo_locked():
            print('WARNING: Locking failed. Timeout expired while trying to obtain lock. ',
                  LockCorrectionThread.UNABLE_TO_LOCK_MESSAGE)
            self.messages.put('stop')

    def restart_timer(self):
        if not self.timer.is_alive():
            self.timer = threading.Timer(self.timeout, self.quit_unless_locked)
            self.timer.start()
