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

recording_length = 400  # in sec

if __name__ == '__main__':
    # Set up recording
    recorder_process = Process(target=record, kwargs={'config': 'from_file', 'length': recording_length, 'TTL': False, 'comment': animal_id + '_' + comment})
    
    # Set up stimulation
    # Using Fujitsu DY22T-7
    # mon = Monitor(resolution=(1920, 1080), dis=60., mon_width_cm=88.6, mon_height_cm=49.8, downsample_rate=4, refresh_rate=60.0)
    mon = Monitor(resolution=(1920, 1080), dis=30., mon_width_cm=47.6, mon_height_cm=26.7, downsample_rate=8, refresh_rate=60.0)

    # The next 2 lines are a workaround for hiding the indicator.
    dummy = Monitor(resolution=(0,0), dis=1, mon_width_cm=1, mon_height_cm=1)
    ind = Indicator(dummy)

    ks = stim.KSstimAllDir(mon, ind, square_size=15, flicker_frame=10, sweep_width=12, step_width=0.20, sweep_frame=1, pregap_dur=2, postgap_dur=1, iteration=10)
    ds = DisplaySequence(log_dir="stimulus", is_by_index=False, display_screen=1, is_sync_pulse_LJ=False)
    
    ds.set_stim(ks)

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
    current_path = Path(os.getcwd())
    log_path = current_path / "stimulus/visual_display_log"
    list_of_files = glob.glob(os.path.normpath(log_path) + "\\*")
    latest_file = max(list_of_files, key=os.path.getctime)
    print(latest_file)

    with open(__file__) as source:
        own_source = source.read()
    save_log_to_recording(latest_file, script_source=own_source)
