from devices import *
from FakeMulticlamp import *
from math import fabs
import time
from threading import Thread, RLock
import numpy as np


class ResistanceMeter(Thread):

    def __init__(self):

        Thread.__init__(self)
        print('Connecting to the MultiClamp amplifier')
        try:
            self.mcc = MultiClamp(channel=1)
        except (AttributeError, RuntimeError):
            print 'No multiclamp detected, switching to fake amplifier.'
            self.mcc = FakeMultiClamp()
        print('Switching to voltage clamp')
        self.mcc.voltage_clamp()
        print('Running automatic slow compensation')
        self.mcc.auto_slow_compensation()
        print('Running automatic fast compensation')
        self.mcc.auto_fast_compensation()

        self.mcc.meter_resist_enable(False)

        self.mcc.set_freq_pulse_amplitude(1e-2)
        self.mcc.set_freq_pulse_frequency(1e-3)
        self.mcc.freq_pulse_enable(False)

        self.mcc.set_primary_signal_membcur()
        self.mcc.set_primary_signal_lpf(2000)
        self.mcc.set_primary_signal_gain(5)
        self.mcc.set_secondary_signal_membpot()
        self.mcc.set_secondary_signal_lpf(2000)
        self.mcc.set_secondary_signal_gain(5)
        time.sleep(1)
        self.mcc.auto_pipette_offset()
        self.mcc.meter_resist_enable(True)
        self.mcc.set_holding(0.)
        self.mcc.set_holding_enable(True)
        self.acquisition = True
        self.continuous = False
        self.discrete = False
        self.res = None

    def run(self):
        while self.acquisition:
            lock = RLock()
            lock.acquire()

            if self.continuous:

                self.mcc.freq_pulse_enable(True)
                while self.continuous:

                    res = []

                    for _ in range(3):
                        res += [self.mcc.get_meter_value().value]
                    self.res = np.mean(res)

                self.mcc.freq_pulse_enable(False)

            elif self.discrete:

                self.mcc.freq_pulse_enable(True)
                res = []

                for _ in range(3):

                    res += [self.mcc.get_meter_value().value]

                self.res = np.mean(res)

                self.mcc.freq_pulse_enable(False)
                self.discrete = False

            else:
                pass

            lock.release()
        self.mcc.set_holding_enable(False)

    def stop(self):
        self.continuous = False
        self.acquisition = False
        time.sleep(.2)

    def start_continuous_acquisition(self):
        self.continuous = True
        self.discrete = False
        time.sleep(.2)

    def stop_continuous_acquisition(self):
        self.continuous = False
        self.discrete = False
        time.sleep(.2)

    def get_discrete_acquisition(self):
        self.continuous = False
        self.discrete = True
        time.sleep(.2)

    def __del__(self):
        self.stop()
        self.mcc.close()


if __name__ == '__main__':
    from matplotlib.pyplot import *
    val = []
    multi = ResistanceMeter()
    multi.start()
    multi.start_continuous_acquisition()
    print('Getting resistance')
    init = time.time()
    while time.time() - init < 5:
        val += [multi.res]
    multi.stop_continuous_acquisition()
    multi.stop()
    print min(val)
    print max(val)
    print np.median(val)
    plot(val)
    show()
    del multi
