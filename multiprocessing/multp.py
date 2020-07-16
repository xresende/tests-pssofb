#!/usr/bin/env python-sirius
"""."""

import time as _time
from threading import Thread as _Thread
import multiprocessing as _mp

from siriuspy.pwrsupply.csdev import PSSOFB_MAX_NR_UDC as _PSSOFB_MAX_NR_UDC
from siriuspy.pwrsupply.csdev import UDC_MAX_NR_DEV as _UDC_MAX_NR_DEV


class PSSOFBBeagle:
    """."""

    SLEEP_IDLE = 0.100  # [s]

    class MODE:
        """."""
        WAIT_IDLE = 0
        RUN_UPDATE = 1
        RUN_SETPOINT = 2
        RUN_SET_UPDATE = 3
        WAIT_REQUEST = 4

    def __init__(self, pid):
        """."""
        self.counter = 0
        self.pid = pid

    def run(self, current, state, nrready):
        """."""
        while True:
            state_ = state[self.pid]
            if state_ == PSSOFBBeagle.MODE.WAIT_IDLE:
                _time.sleep(PSSOFBBeagle.SLEEP_IDLE)
            elif state_ == PSSOFBBeagle.MODE.RUN_UPDATE:
                _time.sleep(0.009)  # task
                with current.get_lock():
                    for i in range(8):
                        current[8*self.pid + i] = 1.0*(self.pid * 8 + i)
                state[self.pid] = PSSOFBBeagle.MODE.WAIT_REQUEST
                with nrready.get_lock():
                    nrready.value += 1
            elif state_ == PSSOFBBeagle.MODE.WAIT_REQUEST:
                pass
            else:
                print('undefined mode!')
                _time.sleep(PSSOFBBeagle.SLEEP_IDLE)


class PSSOFB:
    """."""

    MODE = PSSOFBBeagle.MODE

    SLEEP_TIME = 0.100  # [s]

    BBBNAMES = (
        'IA-01RaCtrl:CO-PSCtrl-SI2',
        'IA-02RaCtrl:CO-PSCtrl-SI2',
        'IA-03RaCtrl:CO-PSCtrl-SI2',
        'IA-04RaCtrl:CO-PSCtrl-SI2',
        'IA-05RaCtrl:CO-PSCtrl-SI2',
        'IA-06RaCtrl:CO-PSCtrl-SI2',
        'IA-07RaCtrl:CO-PSCtrl-SI2',
        'IA-08RaCtrl:CO-PSCtrl-SI2',
        'IA-09RaCtrl:CO-PSCtrl-SI2',
        'IA-10RaCtrl:CO-PSCtrl-SI2',
        'IA-12RaCtrl:CO-PSCtrl-SI2',
        'IA-13RaCtrl:CO-PSCtrl-SI2',
        'IA-14RaCtrl:CO-PSCtrl-SI2',
        'IA-15RaCtrl:CO-PSCtrl-SI2',
        'IA-16RaCtrl:CO-PSCtrl-SI2',
        'IA-17RaCtrl:CO-PSCtrl-SI2',
        'IA-18RaCtrl:CO-PSCtrl-SI2',
        'IA-19RaCtrl:CO-PSCtrl-SI2',
        'IA-20RaCtrl:CO-PSCtrl-SI2',
        'IA-01RaCtrl:CO-PSCtrl-SI4',
        'IA-02RaCtrl:CO-PSCtrl-SI4',
        'IA-03RaCtrl:CO-PSCtrl-SI4',
        'IA-04RaCtrl:CO-PSCtrl-SI4',
        'IA-05RaCtrl:CO-PSCtrl-SI4',
        'IA-06RaCtrl:CO-PSCtrl-SI4',
        'IA-07RaCtrl:CO-PSCtrl-SI4',
        'IA-08RaCtrl:CO-PSCtrl-SI4',
        'IA-09RaCtrl:CO-PSCtrl-SI4',
        'IA-10RaCtrl:CO-PSCtrl-SI4',
        'IA-12RaCtrl:CO-PSCtrl-SI4',
        'IA-13RaCtrl:CO-PSCtrl-SI4',
        'IA-14RaCtrl:CO-PSCtrl-SI4',
        'IA-15RaCtrl:CO-PSCtrl-SI4',
        'IA-16RaCtrl:CO-PSCtrl-SI4',
        'IA-17RaCtrl:CO-PSCtrl-SI4',
        'IA-18RaCtrl:CO-PSCtrl-SI4',
        'IA-19RaCtrl:CO-PSCtrl-SI4',
        'IA-20RaCtrl:CO-PSCtrl-SI4',
    )

    BBB2DEVS = dict()
    _MAX_NR_DEVS = _PSSOFB_MAX_NR_UDC * _UDC_MAX_NR_DEV

    def __init__(self):
        """."""
        self.nrbbbs = len(PSSOFB.BBBNAMES)
        self.nrready = _mp.Value('i', 0)
        self.pstate = _mp.Array('i', self.nrbbbs)
        self.current = _mp.Array('d', self.nrbbbs * 8)
        self._mode = PSSOFB.MODE.WAIT_IDLE
        self.procs = self._process_create()

    def update(self):
        """."""

    def _process_create(self):
        procs = dict()
        def_mode = PSSOFB.MODE.WAIT_IDLE
        for pid in range(len(self.nrbbbs)):
            beagle = PSSOFBBeagle(pid)
            args = (self.current, self.pstate, self.nrready)
            proc = _mp.Process(target=beagle.run, args=args, daemon=True)
            self.pstate[pid] = def_mode
            procs[pid] = proc
            proc.start()
        return procs

    def _set_mode(self, mode):
        """Start beaglebone processes."""
        for pid in self.procs:
            self.pstate[pid] = mode

    def _main_thread_loop(self):
        """."""
        while True:
            if self._running:
                # set nr of procs ready to zero
                t0_ = _time.time()
                with self.nrready.get_lock():
                    self.nrready.value = 0

                # set state of each proc to update
                with self.pstate.get_lock():
                    for pid in range(self.nrbbbs):
                        self.pstate[pid] = PSSOFBBeagle.CMD_UPDATE
                t1_ = _time.time()
                # wait until all processes have completed
                while True:
                    with self.nrready.get_lock():
                        if self.nrready.value == self.nrbbbs:
                            break
                t2_ = _time.time()
                print('time: {:06.3f} {:06.3f} {:06.3f} ms'.format(
                    1000*(t1_-t0_), 1000*(t2_-t1_), 1000*(t2_-t0_)))
                print([v for v in self.current])
                print()
            else:
                _time.sleep(PSSOFB.SLEEP_TIME)


def benchmark():
    """."""
    pssofb = PSSOFB()
    pssofb.start_beagles()
    pssofb.start_master()


if __name__ == "__main__":
    benchmark()
