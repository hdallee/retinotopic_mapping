from multiprocessing import Process
from visexpa.engine.datahandlers.teledyne_camera import record
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping import LaserStim
from retinotopic_mapping.tools.IO.log_file_extraction import save_log_to_recording

animal_id = 'Rat_no57'
comment = ''  # Eg: laser_power_50 or not_dark_adapted etc.

grating_width = 0.1  # in cycles/visual degree
temporal_frequency = 1.5  # in cycles/second

recording_length = 300  # in sec

if __name__ == '__main__':
    # Set up recording
    recorder_process = Process(target=record, kwargs={'config': 'from_file', 'length': recording_length, 'TTL': False,
                                                      'comment': animal_id + '_' + comment})

    # Set up stimulation


    stimulator_process = Process(target=LaserStim.stim_start, kwargs={'animal_id': animal_id, 'laser_power': comment,
                                                                      'rec_length': recording_length})

    # Start recording
    recorder_process.start()
    # Start stimulation
    stimulator_process.start()

    # Ending processes
    recorder_process.join()
    stimulator_process.join()


