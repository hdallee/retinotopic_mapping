import matplotlib.pyplot as plt
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence

mon = Monitor(resolution=(1024, 1280), dis=20., mon_width_cm=33.28, mon_height_cm=26.624, refresh_rate=75)

mon_bin = Monitor(resolution=(0,0), dis=15., mon_width_cm=52., mon_height_cm=32.)

ind = Indicator(mon_bin)

ks = stim.DriftingGratingCircle(mon, ind, radius_list=[50], dire_list=(0., 45., 90., 135., 180., 225., 270.), is_smooth_edge=False, block_dur=3, midgap_dur=2)
ds = DisplaySequence(log_dir="C:/data", is_by_index=True, display_screen=1)

ds.set_stim(ks)
ds.trigger_display(fullscr=True)
# plt.show()