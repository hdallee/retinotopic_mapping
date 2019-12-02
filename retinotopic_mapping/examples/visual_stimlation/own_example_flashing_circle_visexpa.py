import matplotlib.pyplot as plt
import retinotopic_mapping.StimulusRoutines as stim
from retinotopic_mapping.MonitorSetup import Monitor, Indicator
from retinotopic_mapping.DisplayStimulus import DisplaySequence

import sys
import time
import os
import pickle
from visexpA.engine.datahandlers.hdf5io import Hdf5io
from visexpA.engine.misc.introspect import nameless_dummy_object_with_methods
from visexpA.engine.datahandlers.ximea_camera import XimeaCamera
from contextlib import closing

basedir = '/home/abel/data'

camcfg = nameless_dummy_object_with_methods()
file_ts = str(int(time.time()))
save_to_hdf5 = True
if save_to_hdf5:
    outpath = os.path.join(basedir, 'widefield{0}.hdf5'.format(file_ts))
else:
    outpath = os.path.join(basedir, 'widefield/{0}'.format(file_ts))
    os.makedirs(outpath)

experiment_type = 'overview'  # set to 'overview' to acquire only 1 repetition while the camera is focused on the surface of the brain. otherwise 'long'

# stimulus parameters
stimulus_parameters = {}
stimulus_parameters[
    'step_width'] = 0.15  # how many visual degrees the bar is moving per video frame; e.g at 60Hz, 0.15 means the bar is moving at 9 degrees/s speed
stimulus_parameters[
    'sweep_width'] = 20  # how many visual degrees the bar is covering, i.e. longitudinal dimension of the bar
stimulus_parameters[
    'repeat_stimulus'] = 10 if experiment_type != 'overview' else 1  # how many time the stim is played; use 1 for surface scan, 10 when focusing below surface
stimulus_parameters['monitor_width_cm'] = 88.7
stimulus_parameters['monitor_height_cm'] = 49.88
stimulus_parameters['gaze_center_to_monitor_top_edge_cm'] = 33.1
stimulus_parameters['gaze_center_to_monitor_anterior_edge_cm'] = 46.6
camera_downsample = 1 if stimulus_parameters['repeat_stimulus'] == 1 else 2  # default is binning
camcfg.CAMERA = {'simulator': False, 'output': outpath, 'exposure_gain': [28000, 22],
                'width': 1376 / camera_downsample, 'height': 1038 / camera_downsample, 'framerate': 10,
                'downsampling': camera_downsample}
camera = XimeaCamera(config=camcfg) # expected_recording_length=stimulus_parameters['repeat_stimulus'] * 90)
camera.start()

mon = Monitor(resolution=(768, 1360), dis=13.0, mon_width_cm=stimulus_parameters['monitor_width_cm'],
            mon_height_cm=stimulus_parameters['monitor_height_cm'],
            C2T_cm=stimulus_parameters['gaze_center_to_monitor_top_edge_cm'],
            C2A_cm=stimulus_parameters['gaze_center_to_monitor_anterior_edge_cm'],
            visual_field='right', downsample_rate=8)  # 20

indicator = Indicator(mon)
'''
KS_stim_all_dir = stim.KSstimAllDir(mon, indicator, sweep_width=stimulus_parameters['sweep_width'], square_size=25,
                                   flicker_frame=6, iteration=1,
                                   step_width=stimulus_parameters['step_width'], pregap_dur=2.,
                                   postgap_dur=3.)  # stepWidth=0.15, # stepWidth*refreshRate=speed, i.e. 0.15 deg *60 = 9 deg/s
'''
ds = DisplaySequence(log_dir=r'C:\data', display_screen=0, backupdir=None,
                         display_iter=stimulus_parameters['repeat_stimulus'],
                         is_triggered=False, is_sync_pulse=False, is_by_index=False) #, interrupt=camera.camera_error_trigger)
# ds.set_stim(KS_stim_all_dir)
fc = stim.FlashingCircle(monitor=mon, indicator=indicator, coordinate='degree', center=(0., 60.),
                         radius=10., is_smooth_edge=False, smooth_width_ratio=0.2,
                         smooth_func=stim.blur_cos, color=1., flash_frame_num=60,
                         pregap_dur=2., postgap_dur=3., background=-1., midgap_dur=1.,
                         iteration=1)
ds.set_stim(fc)
camera.trigger.set()
time.sleep(0.1)  # let the first camera frames be below target 10Hz (memory allocation or who knows why)
ds.trigger_display()
plt.show()
camera.trigger.clear()

if camera.camera_error_trigger.is_set():  # do not save incomplete data
    print('Experiment stopped due to frame drop in camera.')
    sys.exit(0)
# print('Seconds elapsed between camera stop time and stimulus end: {0}'.format(time.time()-camera.stopped_time))
camera.join()
with closing(Hdf5io(camcfg.CAMERA['output'] if save_to_hdf5 else camcfg.CAMERA['output'] + '/timing.hdf5',
                    filelocking=False)) as output_file:
    output_file.stimulus_parameters = stimulus_parameters
    output_file.stimulus_frame_timestamps = ds.frame_ts_start
    # output_file.stimulusLog = pickle.dumps(ds.seq_log, protocol=4)  # protocol=2
    output_file.stimulusLog = ds.seq_log
    print(output_file.stimulusLog)
    # output_file.stimulusLog = output_file.stimulusLog.decode("utf-8")
    output_file.saving_complete = True
    # output_file.dropped_stimulus_frames = ds.window.nDroppedFrames
    output_file.save(['stimulus_frame_timestamps', 'saving_complete']) # 'stimulusLog', excluded
    output_file.saving_complete = True
    output_file.save('saving_complete')
# print(('Overall, %i frames were dropped.' % ds.window.nDroppedFrames))
print('Data acquisition done. Loading data and averaging frames...')
# pdb.set_trace()
# from matplotlib import pyplot as MPL
from matplotlib import cm
from visexpA.engine.dataprocessors.image import WideFieldData

with closing(WideFieldData(output_file.filename, filelocking=False)) as datahandler:
    camera_mean = datahandler.camera_frames['raw'].mean(axis=0)
plt.imshow(camera_mean, cmap=cm.gray)
plt.show()
from scipy.misc import imsave

imsave(output_file.filename + '.png', camera_mean, 'png')
sys.exit(0)
from visexpA.engine.datadisplay.comparer import yes_no_cancel_question
ans = yes_no_cancel_question(
    'Delete saved files (tap any key to keep them, tap "y" to delete them if this was a test recording',
    show_dialog=True)
if ans == 'y':
    os.remove(output_file.filename)
    os.remove(output_file.filename + '.png')
sys.exit(0)