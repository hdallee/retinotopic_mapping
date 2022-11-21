"""
Record activity evoked by external stimulator device.
Outgoing TTL signal is high in the stimulation period (pulse_width_s) only while camera exposes all sensor lines.
This should enable constraining the stimulation to only a single camera frame(s), making the filtering of stimulation
artifacts easier.
"""
import time
from multiprocessing import Process
from visexpa.engine.datahandlers.teledyne_camera import record
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping import LaserStim
from visexpa.engine.datahandlers.labjack import exposure_synchronized_external_stimulation
from retinotopic_mapping.tools.IO.log_file_extraction import save_extrenal_stim_timestamps_to_recording
from hdf5io.hdf5io import Hdf5io
import glob
import os
from pathlib import Path

animal_id = 'Rat_57'
comment = 'led_power_100'  # Eg: laser_power_50 or not_dark_adapted etc.
stimulator_device = 'NP' # NP if Neurophotometrics laser is used, Prizmatix if Prizmatix LED is used

recording_length = 30  # in sec

target_LED_power = 100
# 'wait_pre_s' has to be at least 3 seconds! Otherwise you might lose a part of the first stimulation.
# 'pulse_width_s' has to be the same length as the stimulation set in Bonsai for the Neurophotometrics laser.
LED_config = cfg = {'wait_pre_s': 3, 'pulse_width_s': 0.2, 'pulse_period_s': 5.0}

folder = time.strftime('%Y.\\%m.%d.\\data')
LED_log_filename = time.strftime('%Y%m%d-%H%M%S-' + comment + '-led_log.pkl')

if __name__ == '__main__':
    # Set up recording
    recorder_process = Process(target=record, kwargs={'config': 'from_file', 'length': recording_length, 'TTL': False,
                                                      'comment': animal_id + '_' + comment})

    # Set up stimulation
    stimulator_process = Process(target=exposure_synchronized_external_stimulation, kwargs={'TTL_config': LED_config,
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

    # Saving stimulation log to recording file
    print("Saving log to recording")
    current_path = os.getcwd()
    current_path = Path(current_path)
    log_path = current_path / "data"
    list_of_files = glob.glob(os.path.normpath(log_path) + "\\*.hdf5")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    with open(__file__) as source:
        own_source = source.read()
    recording = Hdf5io(latest_file)
    save_extrenal_stim_timestamps_to_recording(recording, timestamp_filepath=log_path / LED_log_filename, script_source=own_source)
    recording.close()
