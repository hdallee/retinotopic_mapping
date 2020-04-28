import matplotlib.pyplot as plt
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence

mon = Monitor(resolution=(768, 1360), dis=15., mon_width_cm=52., mon_height_cm=32.)

ind = Indicator(mon)

ks = stim.KSstimAllDir(mon, ind)
ds = DisplaySequence(log_dir="C:/data", is_by_index=False, is_sync_pulse_LJ=False)

ds.set_stim(ks)
ds.trigger_display()
plt.show()