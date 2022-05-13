import time
from multiprocessing import Process
from visexpa.engine.datahandlers.teledyne_camera import record
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping import LaserStim
from visexpa.engine.datahandlers.labjack import LED_stimulation
from retinotopic_mapping.tools.IO.log_file_extraction import save_log_to_recording

animal_id = 'Rat_no58'
comment = 'laser_power_50'  # Eg: laser_power_50 or not_dark_adapted etc.
stimulator_device = 'Prizmatix' # NP if Neurophotometrics laser is used, Prizmatix if Prizmatix LED is used

grating_width = 0.1  # in cycles/visual degree
temporal_frequency = 1.5  # in cycles/second

recording_length = 30  # in sec

target_LED_power = 10
LED_config = cfg = {'wait_pre_s': 0, 'pulse_width_s': 0.2, 'pulse_period_s': 1.0}

folder = time.strftime('%Y.\\%m.%d.\\data')
LED_log_filename = time.strftime('%Y%m%d-%H%M%S-' + comment + '-led_log.pkl')

if __name__ == '__main__':
    # Set up recording
    recorder_process = Process(target=record, kwargs={'config': 'from_file', 'length': recording_length, 'TTL': False,
                                                      'comment': animal_id + '_' + comment})

    # Set up stimulation


    stimulator_process = Process(target=LED_stimulation, kwargs={'TTL_config': LED_config,
                                                                 'target_LED_current': target_LED_power,
                                                                 'len': recording_length,
                                                                 'outfile_path': 'D:\\Data\\Experiment\\' + folder +
                                                                                 '\\' + LED_log_filename})
    # stimulator_process = Process(target=LaserStim.stim_start, kwargs={'animal_id': animal_id, 'laser_power': comment,
    #                                                                   'rec_length': recording_length,
    #                                                                   'stim_device': stimulator_device})

    # Start recording
    recorder_process.start()
    # Start stimulation
    stimulator_process.start()

    # Ending processes
    recorder_process.join()
    stimulator_process.join()


