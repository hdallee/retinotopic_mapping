import os
import glob
from pathlib import Path
from multiprocessing import Process
from visexpa.engine.datahandlers.teledyne_camera import record
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence
from retinotopic_mapping.tools.IO.log_file_extraction import save_log_to_recording

animal_id = 'Rat_no57'
comment = ''  # Eg: laser_power_50 or not_dark_adapted etc.

grating_width = 0.1  # in cycles/visual degree
temporal_frequency = 1.5  # in cycles/second

recording_length = 270  # in sec

if __name__ == '__main__':
    # Set up recording
    recorder_process = Process(target=record, kwargs={'config': 'from_file', 'length': recording_length, 'TTL': False, 'comment': animal_id + '_' + comment})
    
    # Set up stimulation
    # Using Fujitsu DY22T-7
    # mon = Monitor(resolution=(1920, 1080), dis=60., mon_width_cm=88.6, mon_height_cm=49.8, downsample_rate=4, refresh_rate=60.0)
    mon = Monitor(resolution=(1920, 1080), dis=30., mon_width_cm=47.6, mon_height_cm=26.7, downsample_rate=4, refresh_rate=60.0)

    # The next 2 lines are a workaround for hiding the indicator.
    dummy = Monitor(resolution=(0,0), dis=1, mon_width_cm=1, mon_height_cm=1)
    ind = Indicator(dummy)

    dg = stim.DriftingGratingCircle(mon, ind, radius_list=[50], dire_list=[0, 90, 180, 270],
                                    pregap_dur=5, postgap_dur=7, is_smooth_edge=False, block_dur=6, midgap_dur=7,
                                    center=(0., 60.), sf_list=[grating_width], tf_list=[temporal_frequency],
                                    con_list=[1.], iteration=5, is_blank_block=False, sqr=True)
    ds = DisplaySequence(log_dir="stimulus", is_by_index=True, display_screen=1, is_sync_pulse_LJ=False)
    ds.set_stim(dg)

    stimulator_process = Process(target=ds.trigger_display, kwargs={'fullscr': True})

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
    log_path = current_path / "stimulus/visual_display_log"
    list_of_files = glob.glob(os.path.normpath(log_path) + "\\*")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    save_log_to_recording(latest_file)
