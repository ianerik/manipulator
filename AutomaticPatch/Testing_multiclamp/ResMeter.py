from devices import *
import nidaqmx
from math import fabs
import time


class ResistanceMeter:

    def __init__(self):

        print('Connecting to the MultiClamp amplifier')
        self.mcc = MultiClamp(channel=1)
        print('Switching to voltage clamp')
        self.mcc.voltage_clamp()
        print('Running automatic slow compensation')
        self.mcc.auto_slow_compensation()
        print('Running automatic fast compensation')
        self.mcc.auto_fast_compensation()

        mcc.meter_resist_enable(False)

        self.mcc.set_freq_pulse_amplitude(1e-2)
        self.mcc.set_freq_pulse_frequency(1e-2)

        self.mcc.set_primary_signal_membcur()
        self.mcc.set_primary_signal_lpf(1000)
        self.mcc.set_primary_signal_gain(5)
        self.mcc.set_secondary_signal_membpot()
        self.mcc.set_secondary_signal_lpf(1000)
        time.sleep(1)

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            self.init = task.read()

        self.mcc.auto_pipette_offset()

    def get_res(self):

        n = 0
        res = []

        self.mcc.freq_pulse_enable(True)
        init_time = time.time()

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0")
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            while n < 5:
                temp = task.read()
                if fabs(temp[0] - init[0]) > 1:
                    res += [fabs((temp[1]/10.)/(5*1e-9*temp[0]/0.5))]
                    n += 1

        self.mcc.freq_pulse_enable(False)
        print('Time: {}'.format(time.time()-init_time))

        return sum(res)/len(res)

    def __del__(self):
        self.mcc.close()

if __name__ == '__main__':
    multi = ResistanceMeter()
    print('Resistance is:{}'.format(multi.get_res()))
    del multi
