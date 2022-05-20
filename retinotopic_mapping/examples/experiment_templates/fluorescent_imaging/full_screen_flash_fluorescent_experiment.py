import os
import glob
import time
from pathlib import Path
from multiprocessing import Process
from visexpa.engine.datahandlers.teledyne_camera import record
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence
from retinotopic_mapping.tools.IO.log_file_extraction import save_log_to_recording

animal_id = 'Rat_no57'
comment = ''  # Eg: laser_power_50 or not_dark_adapted etc.

# grating_width = 0.1  # in cycles/visual degree
temporal_frequency = 2  # in Hz

recording_length = 60  # in sec
wait_before = 10  # in sec, record before stimulation starts
stop_before = 10  # in sec, stop stimulation before recording

stim_num = temporal_frequency * recording_length - (temporal_frequency * stop_before * 2)

blocks = False

# Do not change these lines!
period = 1 / temporal_frequency
stim_period = period / 2
flash_frame_number = int(stim_period * 60)


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

    # dg = stim.DriftingGratingCircle(mon, ind, radius_list=[50], dire_list=[0, 90, 180, 270],
    #                                 pregap_dur=3, postgap_dur=3, is_smooth_edge=False, block_dur=4, midgap_dur=3,
    #                                 center=(0., 60.), sf_list=[grating_width], tf_list=[temporal_frequency],
    #                                 con_list=[1.], iteration=10, is_blank_block=False, sqr=True)

    uc = stim.UniformContrast(mon, ind, duration=stim_period, color=1)
    fc = stim.FlashingCircle(mon, ind, center=(0., 60.), radius=50., color=1, midgap_dur=stim_period, iteration=5,
                             flash_frame_num=flash_frame_number)
    if blocks:
        repeated_stim = stim.CombinedStimuli(mon, ind, background=-1, pregap_dur=3, postgap_dur=0)
        repeated_stim.set_stimuli([fc] * int(stim_num/5)) # set the number of iterations here
    else:
        repeated_stim = stim.CombinedStimuli(mon, ind, background=-1, pregap_dur=stim_period, postgap_dur=0)
        repeated_stim.set_stimuli([uc]*stim_num)  # set the number of iterations here

    ds = DisplaySequence(log_dir="stimulus", is_by_index=True, display_screen=1, is_sync_pulse_LJ=False)
    ds.set_stim(repeated_stim)

    stimulator_process = Process(target=ds.trigger_display, kwargs={'fullscr': True})

    # Start recording
    recorder_process.start()
    # Start stimulation
    time.sleep(wait_before)
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

    with open(__file__) as source:
        own_source = source.read()
    save_log_to_recording(latest_file, script_source=own_source)

