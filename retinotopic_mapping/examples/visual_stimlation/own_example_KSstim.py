import matplotlib.pyplot as plt
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence

mon = Monitor(resolution=(768, 1360), dis=15., mon_width_cm=52., mon_height_cm=32.)

ind = Indicator(mon)

# ks = stim.KSstim(mon, ind)
ds = DisplaySequence(log_dir="C:/data", is_by_index=False)

# ds.set_stim(ks)
fc = stim.FlashingCircle(monitor=mon, indicator=ind, coordinate='degree', center=(0., 60.),
                         radius=10., is_smooth_edge=False, smooth_width_ratio=0.2,
                         smooth_func=stim.blur_cos, flash_frame_num=60,
                         pregap_dur=2., postgap_dur=3., midgap_dur=1.,
                         iteration=1)
ds.set_stim(fc)
ds.trigger_display(fullscr=True)
plt.show()