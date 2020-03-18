import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence


mon = Monitor(resolution=(1024, 1280), dis=20., mon_width_cm=33.28, mon_height_cm=26.624, refresh_rate=60.0)

# creating a monitor object to display the indicator on (since we don' use it)
mon_bin = Monitor(resolution=(0,0), dis=15., mon_width_cm=52., mon_height_cm=32.)
ind = Indicator(mon_bin)

uc = stim.UniformContrast(mon, ind, duration=2, color=1)
stimulus = [uc]
repeated_stim = stim.CombinedStimuli(mon, ind, background=-1, pregap_dur=2, postgap_dur=0)
repeated_stim.set_stimuli(stimulus*10) # set the number of iterations here

ds = DisplaySequence(log_dir="C:/data", is_by_index=True, display_screen=1, is_sync_pulse_LJ=True)

ds.set_stim(repeated_stim)
ds.trigger_display(fullscr=False)