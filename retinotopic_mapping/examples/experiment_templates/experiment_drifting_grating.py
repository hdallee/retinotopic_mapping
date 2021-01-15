import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence

if __name__ == "__main__":
    mon = Monitor(resolution=(1920, 1080), dis=60., mon_width_cm=88.6, mon_height_cm=49.8, refresh_rate=60.0)

    # creating a monitor object to display the indicator on (since we don' use it)
    mon_bin = Monitor(resolution=(0,0), dis=15., mon_width_cm=52., mon_height_cm=32.)
    ind = Indicator(mon_bin)

    ks = stim.DriftingGratingCircle(mon, ind, radius_list=[50], dire_list=[0, 45, 90, 135, 180, 225, 270, 315],
                                    pregap_dur=3, postgap_dur=2, is_smooth_edge=False, block_dur=5, midgap_dur=5,
                                    center=(0., 60.), sf_list=[0.05], tf_list=[0.8], con_list=[1], iteration=5,
                                    is_blank_block=False, sqr=False)
    ds = DisplaySequence(log_dir="/data", is_by_index=True, display_screen=0, is_sync_pulse_LJ=False)

    ds.set_stim(ks)
    ds.trigger_display(fullscr=True)

    # frame_start = ds.frame_ts_start
    # print(frame_start[:100])
    # frame_end = ds.frame_ts_end
