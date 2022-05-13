from visexpa.engine.datahandlers.labjack import U3Wrap
import time
import pickle

def stim_pulse(pulse_number, pulse_freq, pulse_width, lj):
    for i in range(pulse_number):
        lj.jack.setDIOState(IOnum=0, state=1)
        time.sleep(pulse_width)
        lj.jack.setDIOState(IOnum=0, state=0)
        time.sleep(1/pulse_freq)

def stim_start(animal_id, laser_power, rec_length, stim_device='NP'):
    labjack = U3Wrap()
    labjack.jack.setDIOState(IOnum=0, state=0)
    stim_start_times = []
    t0 = time.time()
    time.sleep(2)
    if stim_device == 'NP':
        while time.time() - t0 < rec_length:
            labjack.jack.setDIOState(IOnum=0, state=1)
            stim_start_times.append(time.time())
            print('Started NP laser stimulation.')
            time.sleep(0.01)
            labjack.jack.setDIOState(IOnum=0, state=0)
            time.sleep(10)
    elif stim_device == 'Prizmatix':
        pulse_number = 25
        pulse_freq = 5
        pulse_width = 0.002
        while time.time() - t0 < rec_length:
            print('Started Prizmatix LED stimulation.')
            stim_start_times.append(time.time())
            stim_pulse(pulse_number, pulse_freq, pulse_width, labjack)
            time.sleep(10)
    format = '%Y%m%d-%H%M%S'
    save_time = time.strftime(format, time.localtime(t0))
    filename = save_time + '_' + animal_id + '_' + laser_power + '_stimulation_starts' + '.pickle'
    file = open(filename, 'wb')
    pickle.dump(stim_start_times, file)
    file.close()