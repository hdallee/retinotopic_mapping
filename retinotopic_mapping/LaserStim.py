from visexpa.engine.datahandlers.labjack import U3Wrap
import time
import pickle



def stim_start(animal_id, laser_power, rec_length):
    labjack = U3Wrap()
    labjack.jack.setDIOState(IOnum=0, state=0)
    stim_start_times = []
    t0 = time.time()
    time.sleep(2)
    while time.time() - t0 < rec_length:
        labjack.jack.setDIOState(IOnum=0, state=1)
        stim_start_times.append(time.time())
        print('Started laser stimulation.')
        time.sleep(0.01)
        labjack.jack.setDIOState(IOnum=0, state=0)
        time.sleep(10)
    format = '%Y%m%d-%H%M%S'
    save_time = time.strftime(format, time.localtime(t0))
    filename = save_time + '_' + animal_id + '_' + laser_power + '_stimulation_starts' + '.pickle'
    file = open(filename, 'wb')
    pickle.dump(stim_start_times, file)
    file.close()