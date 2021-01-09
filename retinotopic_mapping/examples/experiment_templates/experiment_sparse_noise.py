import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('TkAgg')

if __name__ == '__main__':
    mon = Monitor(resolution=(600, 800), dis=20., mon_width_cm=2, mon_height_cm=1.5, refresh_rate=60.0)

    # mon.plot_map()
    # plt.show()

    # creating a monitor object to display the indicator on (since we don' use it)
    mon_bin = Monitor(resolution=(0, 0), dis=15., mon_width_cm=52., mon_height_cm=32.)
    ind = Indicator(mon_bin, width_cm=3, height_cm=3, is_sync=True, freq=1)

    sparse_noise = stim.SparseNoise(mon, ind, grid_space=(0.5, 0.5), probe_size=(0.5, 0.5),
                                    probe_frame_num=6, coordinate='linear', midgap_dur=0.5, iteration=5)

    ds = DisplaySequence(log_dir="data", is_by_index=True, display_screen=1, is_sync_pulse_LJ=False)

    ds.set_stim(sparse_noise)
    ds.trigger_display(fullscr=False)
