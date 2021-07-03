'''
2017-10-31 by Jun Zhuang
this module provides analysis tools to extract information about visual stimuli
saved in the log pkl files.
'''

import warnings
import os
from pathlib import Path
import numpy as np
import json
import pickle
import retinotopic_mapping.tools.FileTools as ft
import retinotopic_mapping.tools.GenericTools as gt
from retinotopic_mapping.tools.IO.LogFileExtractorTools import extract_dir_order_of_iteration

class DisplayLogAnalyzer(object):
    """
    class to take display_log (.pkl) file, check its integrity and extract stimuli and display
    organize into stim_dict dictionary, which is a intermediate step to put visual display
    information into nwb files.
    """

    def __init__(self, log_path):

        self.log_path = log_path
        self.log_dict = ft.loadFile(log_path)

        if not self.log_dict['presentation']['is_by_index']:
            warnings.warn('The visual stimuli display should be indexed.')
        else:
            self.check_integrity()

        self.stim_type = self.log_dict['stimulation']['stim_name']
        if not self.stim_type == 'CombinedStimuli':
            self.iteration = self.log_dict['stimulation']['iteration']
        else:
            self.iteration = len(self.log_dict['stimulation']['stimuli_sequence'])

    def check_integrity(self):

        print(self.log_dict['presentation']['frame_stats'])

        if not self.log_dict['presentation']['keep_display']:
            raise ValueError('Stimulus presentation did not end normally.')

        total_frame1 = len(self.log_dict['presentation']['displayed_frames'])
        total_frame2 = len(self.log_dict['presentation']['frame_ts_start'])
        total_frame3 = len(self.log_dict['presentation']['frame_ts_end'])
        total_frame4 = len(self.log_dict['stimulation']['index_to_display'])
        if not total_frame1 == total_frame2 == total_frame3 == total_frame4:
            print('\nNumber of displayed frames: {}.'.format(total_frame1))
            print('\nNumber of frame start timestamps: {}.'.format(total_frame2))
            print('\nNumber of frame end timestamps: {}.'.format(total_frame3))
            print('\nNumber of frames to be displayed: {}.'.format(total_frame4))
            raise ValueError('Numbers of total frames do not agree with each other from various places.')

        if max(self.log_dict['stimulation']['index_to_display']) >= \
                len(self.log_dict['stimulation']['frames_unique']):
            raise ValueError('Display index beyond number of unique frames.')

        if self.log_dict['stimulation']['stim_name'] == 'CombinedStimuli':
            stimuli_sequence_out = [f[0] for f in self.log_dict['presentation']['displayed_frames']]
            stimuli_sequence_out = list(set(stimuli_sequence_out))
            stimuli_sequence_out.sort()
            stimuli_sequence_in = list(self.log_dict['stimulation']['individual_logs'].keys())
            stimuli_sequence_in.sort()
            if stimuli_sequence_out != stimuli_sequence_in:
                raise ValueError('Output stimuli sequence does not match input stimuli sequence.')

    @property
    def num_frame_tot(self):
        return len(self.log_dict['presentation']['displayed_frames'])

    def get_stim_dict(self):
        """
        Returns
        -------
        stim_dict: dictionary
            the structure of this dictionary should look like this:

            {
             '000_UniformContrastRetinotopicMapping': {
                                                       ...
                                                       'stim_name' : '000_UniformContrastRetinotopicMapping',
                                                       'index_to_display': <index referencing 'frames_unique' field>
                                                       'timestamps': <index referencing entire display sequence,
                                                                     should match hardware vsync signal>
                                                       'frames_unique': list of tuple representing unique frames
                                                       ...
                                                       },
             '001_StimulusSeparatorRetinotopicMapping: {
                                                        ...
                                                        'stim_name' : '000_UniformContrastRetinotopicMapping',
                                                        'index_to_display': <index referencing 'frames_unique' field>
                                                        'timestamps': <index referencing entire display sequence,
                                                                       should match hardware vsync signal>
                                                        'frames_unique': list of tuple representing unique frames
                                                        ...
                                                        },
             ...
             }
        """

        comments = ''
        description = ''
        source = 'retinotopic_mapping package'
        stim_dict = {}

        # if multiple stimuli were displayed in a sequence
        if self.log_dict['stimulation']['stim_name'] == 'CombinedStimuli':
            curr_frame_ind = 0
            stim_ids = list(self.log_dict['stimulation']['individual_logs'].keys())
            stim_ids.sort()
            for stim_id in stim_ids:
                curr_dict = self.log_dict['stimulation']['individual_logs'][stim_id]
                curr_stim_name = stim_id + 'RetinotopicMapping'
                curr_dict['stim_name'] = curr_stim_name
                curr_num_frames = len(curr_dict['index_to_display'])
                curr_dict.update({'timestamps': np.arange(curr_num_frames, dtype=np.uint64) + curr_frame_ind,
                                  'comments': comments,
                                  'source': source,
                                  'description': description})
                curr_frame_ind = curr_frame_ind + curr_num_frames
                stim_dict.update({curr_stim_name: curr_dict})

        # if only one stimulus was displayed
        else:
            stim_name = self.log_dict['stimulation']['stim_name']
            if stim_name in ['UniformContrast', 'FlashingCircle', 'SparseNoise', 'LocallySparseNoise',
                             'DriftingGratingCircle', 'StaticGratingCircle', 'StaticImages', 'StimulusSeparator',
                             'SinusoidalLuminance']:
                curr_stim_name = '{:03d}_{}RetinotopicMapping'.format(0, stim_name)
                curr_dict = self.log_dict['stimulation']
                curr_dict['stim_name'] = curr_stim_name
                curr_dict.update({'timestamps': np.arange(self.num_frame_tot, dtype=np.uint64)})
            else:
                raise NotImplementedError('Do not understand stimulus: {}.'.format(stim_name))

            curr_dict.update({'comments': comments,
                              'source': source,
                              'description': description})
            stim_dict.update({curr_stim_name : curr_dict})

        return stim_dict

    def stim_block_extractor(self):
        """
        Extract stimulus index and timestamp information from the log, and store it in the object's
        iteration_indices/direction_indices and iteration_timestamps/direction_timestamps attribute.

        Returns
        -------
        None

        """
        if self.stim_type == 'DriftingGratingCircle':
            self.direction = [str(dir) for dir in self.log_dict['stimulation']['dire_list']]
            self.direction_indices = {}
            self.direction_timestamps = {}
            for direction in self.direction:
                self.direction_indices[direction] = []
                self.direction_timestamps[direction] = []
            for i in range(len(self.log_dict['presentation']['displayed_frames'])):
                if self.log_dict['presentation']['displayed_frames'][i][0] > \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    iteration_first_index = i
                elif self.log_dict['presentation']['displayed_frames'][i][0] < \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    self.direction_timestamps[str(self.log_dict['presentation']['displayed_frames'][i - 1][4])].append(
                        (self.log_dict['presentation']['frame_ts_start'][iteration_first_index],
                         self.log_dict['presentation']['frame_ts_end'][i - 1]))
                    self.direction_indices[str(self.log_dict['presentation']['displayed_frames'][i - 1][4])].append(
                        (iteration_first_index, i-1))

        elif self.stim_type == 'KSstim':
            self.direction = self.log_dict['stimulation']['direction']
            self.iteration_indices = []
            self.iteration_timestamps = []
            for i in range(len(self.log_dict['presentation']['displayed_frames'])):
                if self.log_dict['presentation']['displayed_frames'][i][0] > \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    iteration_first_index = i
                elif self.log_dict['presentation']['displayed_frames'][i][0] < \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    iteration_last_index = i-1
                    self.iteration_timestamps.append((self.log_dict['presentation']['frame_ts_start'][iteration_first_index],
                                                      self.log_dict['presentation']['frame_ts_start'][iteration_last_index]))
                    self.iteration_indices.append((iteration_first_index, iteration_last_index))

            if not len(self.iteration_timestamps) == self.iteration:
                ValueError("Couldn't extract timestamps of all iterations.")

        elif self.stim_type == 'KSstimAllDir':
            self.direction = self.log_dict['stimulation']['direction']
            self.direction_indices = {}
            self.direction_timestamps = {}
            for direction in self.direction:
                self.direction_indices[direction] = []
                self.direction_timestamps[direction] = []
            for i in range(len(self.log_dict['presentation']['displayed_frames'])):
                if self.log_dict['presentation']['displayed_frames'][i][0] > \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    iteration_first_index = i
                elif self.log_dict['presentation']['displayed_frames'][i][0] < \
                        self.log_dict['presentation']['displayed_frames'][i - 1][0]:
                    self.direction_timestamps[self.log_dict['presentation']['displayed_frames'][i-1][4]].append(
                        (self.log_dict['presentation']['frame_ts_start'][iteration_first_index],
                         self.log_dict['presentation']['frame_ts_end'][i-1]))
                    self.direction_indices[self.log_dict['presentation']['displayed_frames'][i - 1][4]].append(
                        (iteration_first_index, i - 1))

        elif self.stim_type == 'CombinedStimuli':
            self.stimuli_sequence = self.log_dict['stimulation']['stimuli_sequence']
            is_UniformContrast = True
            for name in self.stimuli_sequence:
                if 'UniformContrast' not in name:
                    is_UniformContrast = False
            if is_UniformContrast:
                self.iteration_indices = []
                self.iteration_timestamps = []
                block_started = False
                for i in range(len(self.log_dict['presentation']['displayed_frames'])):
                    if self.log_dict['presentation']['displayed_frames'][i][1] > \
                            self.log_dict['presentation']['displayed_frames'][i - 1][1]:
                        iteration_first_index = i
                        block_started = True
                    elif (block_started and self.log_dict['presentation']['displayed_frames'][i][1] <
                          self.log_dict['presentation']['displayed_frames'][i - 1][1]) or \
                            (block_started and i == len(self.log_dict['presentation']['displayed_frames'])-1):
                        iteration_last_index = i - 1
                        self.iteration_timestamps.append((self.log_dict['presentation']['frame_ts_start'][iteration_first_index],
                                                          self.log_dict['presentation']['frame_ts_start'][iteration_last_index]))
                        self.iteration_indices.append((iteration_first_index, iteration_last_index))
                        block_started = False  # we found the end of the stim block
            else:
                print('Combined stimuli that are not Uniform Contrast are not implemented yet.')

    def save_to_recording(self, recording_full_path=None):
        """
        Search for the corresponding .hdf recording file and save the stimulus log and the extracted variables to it.
        Intended to be run after using stim_block_extractor().
        """
        from visexpa.engine.datahandlers.hdf5io import Hdf5io
        if recording_full_path is None:  # Tries to find corresponding recording based on timestamp in filename.
            experiment_folder = str(self.log_path)[:str(self.log_path).find('stimulus') - 1]
            self.recording_path = Path(experiment_folder) / 'data'
            log_ts_str = str(self.log_path.stem)[6:12]
            found_file_counter = 0
            for filename in os.listdir(self.recording_path):
                if filename[-4:] == 'hdf5' and abs(ft.time_diff_in_seconds(log_ts_str, filename[9:15])) < 20:
                    recording_full_path = self.recording_path / filename
                    found_file_counter += 1
            if found_file_counter != 1:
                raise ValueError('Cannot determine corresponding recording file, please specify it with the filename!')

        with Hdf5io(filename=str(recording_full_path), filelocking=False) as recording:
            print(recording.h5f)
            if self.stim_type == 'KSstimAllDir' or self.stim_type == 'DriftingGratingCircle':
                try:
                    print('Saving')
                    #  save direction_timestamps
                    recording.direction_timestamps = self.direction_timestamps
                    recording.stim_parameters = {}
                    recording.stim_parameters['iteration'] = self.iteration
                    recording.stim_parameters['directions'] = self.direction
                    recording.stim_parameters['stim_type'] = self.stim_type
                    recording.stim_parameters['num_frame_tot'] = self.num_frame_tot

                    recording.save(['direction_timestamps', 'stim_parameters'])
                except IOError:
                    print('Saving was unsuccessful.')

            elif self.stim_type == 'KSstim':
                try:
                    print('Saving')
                    recording.iteration_timestamps = self.iteration_timestamps
                    recording.stim_parameters = {}
                    recording.stim_parameters['iteration'] = self.iteration
                    recording.stim_parameters['directions'] = self.direction
                    recording.stim_parameters['stim_type'] = self.stim_type
                    recording.stim_parameters['num_frame_tot'] = self.num_frame_tot

                    recording.save(['iteration_timestamps', 'stim_parameters'])

                except IOError:
                    print('Saving was unsuccessful.')

            elif self.stim_type == 'CombinedStimuli':
                self.stimuli_sequence = self.log_dict['stimulation']['stimuli_sequence']
                is_UniformContrast = True
                for name in self.stimuli_sequence:
                    if 'UniformContrast' not in name:
                        is_UniformContrast = False
                if is_UniformContrast:
                    try:
                        print('Saving')
                        recording.iteration_timestamps = self.iteration_timestamps
                        recording.stim_parameters = {}
                        recording.stim_parameters['iteration'] = self.iteration
                        recording.stim_parameters['stim_type'] = self.stim_type
                        recording.stim_parameters['num_frame_tot'] = self.num_frame_tot

                        recording.save(['iteration_timestamps', 'stim_parameters'])

                    except IOError:
                        print('Saving was unsuccessful.')

            else:
                print("Saving this stimulus type is not implemented yet.")

            # Dump whole stimulation log to hdf5 file in pickled format
            recording.stim_log = pickle.dumps(self.log_dict)
            recording.save(['stim_log'])

    def save_to_json(self):
        """
        Save stimulus parameters to .json file in the original log's folder.

        Notes
        -----
        Intended to be run after using stim_block_extractor().

        Returns
        -------
        None

        """
        outfile_name = str(self.log_path)[:-3] + 'json'
        with open(outfile_name, 'w') as outfile:
            if self.stim_type == 'KSstimAllDir' or self.stim_type == 'DriftingGratingCircle':
                try:
                    data = {}
                    data["direction_indices"] = self.direction_indices
                    data["directon_timestamps"] = self.direction_timestamps
                    data["stim_parameters"] = {}
                    data["stim_parameters"]["iteration"] = self.iteration
                    data["stim_parameters"]["directions"] = self.direction
                    data["stim_parameters"]["stim_type"] = self.stim_type
                    data["stim_parameters"]["num_frame_tot"] = self.num_frame_tot

                    print('Saving')
                    #  save direction_timestamps
                    json.dump(data, outfile, sort_keys=True, indent=4)

                except IOError:
                    print('Saving was unsuccessful.')

            elif self.stim_type == 'CombinedStimuli':
                self.stimuli_sequence = self.log_dict['stimulation']['stimuli_sequence']
                is_UniformContrast = True
                for name in self.stimuli_sequence:
                    if 'UniformContrast' not in name:
                        is_UniformContrast = False
                if is_UniformContrast:
                    try:
                        data = {}
                        data["iteration_indices"] = self.iteration_indices
                        data["iteration_timestamps"] = self.iteration_timestamps
                        data["stim_parameters"] = {}
                        data["stim_parameters"]["iteration"] = self.iteration
                        data["stim_parameters"]["stim_type"] = self.stim_type
                        data["stim_parameters"]["num_frame_tot"] = self.num_frame_tot
                        print('Saving')
                        json.dump(data, outfile, sort_keys=True, indent=4)

                    except IOError:
                        print('Saving was unsuccessful.')

            else:
                print("Saving this stimulus type is not implemented yet.")


    def analyze_photodiode_onsets_sequential(self, stim_dict, pd_thr=-0.5):
        """
        Analyze photodiode onsets in a sequential way

        Parameters
        ----------
        stim_dict: dictionary
            should be the output of self.get_stim_dict()

        pd_thr : float
            the threshold to detect photodiode onset, the photodiode color was saved in each displayed frame (the
            last item of frame tuple) as float with range [-1., 1.]. pd_onset is defined as up crossing the pd_thr.
            retinotopic_mapping.tools.GenericTools.up_crossing() function is used to detect the up crossing. It
            detects the frame meeting the following criteria: 1) the current frame has photodiode color larger than
            pd_thr; 2) the previous frame has photodiode color no larger than pd_thr

        Returns
        -------
        pd_onsets: list
            list of photodiode onsets in sequential manner (in time). Each element in the list is a dictionary
            representing one photodiode onset. The dictionary has 3 fields:
                1. stim_name: str, the name of the stimulus the onset belongs to
                2. global_frame_ind: the index of this frame in the total frame displayed
                3. global_pd_onset_ind: the index of this photodiode onset in the total photodiode onsets series
                                        of the stimuli display
                4. str(s)_stim: string that represents the properties of the onset frame. For most frame it is just a
                            string, for LocallySparseNoise, it is a set of strings with each string representing one
                            probe on the onset frame.
        """

        print('\nAnalyzing photodiode onsets in a sequential manner ...')

        stim_ns = list(stim_dict.keys())
        stim_ns.sort()

        pd_onsets_seq = []

        global_pd_onset_ind = 0
        for stim_n in stim_ns:

            curr_stim_dict = stim_dict[stim_n]
            curr_stim_n = curr_stim_dict['stim_name']

            # print('\n{}'.format(curr_stim_n))

            curr_stim_pd_onsets = []

            pd_trace_unique = np.array([f[-1] for f in curr_stim_dict['frames_unique']])
            index_to_display = np.array(curr_stim_dict['index_to_display'], dtype=np.uint64)
            pd_trace = pd_trace_unique[index_to_display]
            pd_onset_indices = gt.up_crossings(data=pd_trace, threshold=pd_thr)

            for pd_onset_ind in pd_onset_indices:
                onset_frame = curr_stim_dict['frames_unique'][curr_stim_dict['index_to_display'][pd_onset_ind]]
                # print(onset_frame)

                curr_pd_onset = {'stim_name': curr_stim_n,
                                 'global_frame_ind': curr_stim_dict['timestamps'][pd_onset_ind],
                                 'global_pd_onset_ind': global_pd_onset_ind}

                if curr_stim_n[-34:] == '_UniformContrastRetinotopicMapping':
                    str_uc = 'color{:05.2f}'.format(curr_stim_dict['color'])
                    curr_pd_onset.update({'str_stim': str_uc})
                elif curr_stim_n[-36:] == '_StimulusSeparatorRetinotopicMapping':
                    curr_pd_onset.update({'str_stim': 'color1'})
                elif curr_stim_n[-33:] == '_FlashingCircleRetinotopicMapping':
                    str_fc = 'alt{:06.1f}_azi{:06.1f}_color{:05.2f}_rad{:05.1f}'\
                        .format(curr_stim_dict['center'][0],
                                curr_stim_dict['center'][1],
                                curr_stim_dict['color'],
                                float(curr_stim_dict['radius']))
                    curr_pd_onset.update({'str_stim': str_fc})
                elif curr_stim_n[-30:] == '_SparseNoiseRetinotopicMapping':
                    str_sn_probe = 'alt{:06.1f}_azi{:06.1f}_sign{:02d}'\
                        .format(onset_frame[1][0], onset_frame[1][1], int(onset_frame[2]))
                    curr_pd_onset.update({'str_stim': str_sn_probe})
                elif curr_stim_n[-37:] == '_LocallySparseNoiseRetinotopicMapping':
                    str_lsn_probes = []
                    for probe in onset_frame[1]:
                        str_lsn_probes.append('alt{:06.1f}_azi{:06.1f}_sign{:02d}'
                                              .format(probe[0], probe[1], int(probe[2])))
                    str_lsn_probes = set(str_lsn_probes)
                    curr_pd_onset.update({'strs_stim': str_lsn_probes})
                elif curr_stim_n[-40:] == '_DriftingGratingCircleRetinotopicMapping':
                    str_dgc = 'alt{:06.1f}_azi{:06.1f}_sf{:04.2f}_tf{:04.1f}_dire{:03d}_con{:04.2f}_rad{:03d}'\
                        .format(curr_stim_dict['center'][0],
                                curr_stim_dict['center'][1],
                                onset_frame[2],
                                onset_frame[3],
                                int(onset_frame[4]),
                                onset_frame[5],
                                int(onset_frame[6]))
                    curr_pd_onset.update({'str_stim': str_dgc})
                elif curr_stim_n[-38:] == '_StaticGratingCircleRetinotopicMapping':
                    str_sgc = 'alt{:06.1f}_azi{:06.1f}_sf{:04.2f}_phase{:03d}_ori{:03d}_con{:04.2f}_rad{:03d}'.\
                        format(curr_stim_dict['center'][0],
                               curr_stim_dict['center'][1],
                               onset_frame[1],
                               int(onset_frame[2]),
                               int(onset_frame[3]),
                               onset_frame[4],
                               int(onset_frame[5]))
                    curr_pd_onset.update({'str_stim': str_sgc})
                elif curr_stim_n[-31:] == '_StaticImagesRetinotopicMapping':
                    str_si = 'img_ind{:05d}'.format(onset_frame[1])
                    curr_pd_onset.update({'str_stim': str_si})
                elif curr_stim_n[-38:] == '_SinusoidalLuminanceRetinotopicMapping':
                    str_sl = 'onset'
                    curr_pd_onset.update({'str_stim': str_sl})
                else:
                    raise LookupError('Do not understand stimulus name: {}'.format(curr_stim_n))

                curr_stim_pd_onsets.append(curr_pd_onset)
                global_pd_onset_ind = global_pd_onset_ind + 1

            print('{:<45}: number of photodiode_onset: {}'.format(curr_stim_n, len(curr_stim_pd_onsets)))
            pd_onsets_seq = pd_onsets_seq + curr_stim_pd_onsets

        # print('\n'.join([str(pd) for pd in pd_onsets]))
        print('\nTotal number of expected photodiode onsets: {}'.format(len(pd_onsets_seq)))

        # sanity check of global_pd_onset_ind
        # for i, po in enumerate(pd_onsets):
        #     assert (i == po['global_pd_onset_ind'])

        return pd_onsets_seq

    def analyze_photodiode_onsets_combined(self, pd_onsets_seq, is_dgc_blocked=True):
        """

        Parameters
        ----------
        pd_onsets_seq: list
            product of self.analyze_photodiode_onsets_sequential()

        dgc_onset_type : str
            type of onset "block" or "cycle"

        returns
        -------
        pd_onsets_combined : dict
        """

        stim_ns = [po['stim_name'] for po in pd_onsets_seq]
        stim_ns = list(set(stim_ns))
        stim_ns.sort()

        # print('\n'.join(stim_ns))

        pd_onsets_combined = {}

        for stim_n in stim_ns:
            curr_pd_onsets_seq = [po for po in pd_onsets_seq if po['stim_name'] == stim_n]
            # print(len(curr_pd_onsets))

            curr_pd_onsets_com = {}

            if stim_n[-34:] == '_UniformContrastRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-36:] == '_StimulusSeparatorRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-33:] == '_FlashingCircleRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-30:] == '_SparseNoiseRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-37:] == '_LocallySparseNoiseRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_locally_sparse_noise(curr_pd_onsets_seq))
            elif stim_n[-40:] == '_DriftingGratingCircleRetinotopicMapping':
                dgc_pd_onsets_com = self._analyze_pd_onset_combined_drifting_grating_circle(curr_pd_onsets_seq)

                if is_dgc_blocked:
                    fs = self.log_dict['monitor']['refresh_rate']
                    dgc_log_dict = self._get_dgc_log_dict(dgc_name=stim_n)
                    block_dur = dgc_log_dict['block_dur']
                    # midgap_dur = dgc_log_dict['midgap_dur']
                    iteration = dgc_log_dict['iteration']
                    block_frame_num = int(fs * block_dur)

                    for dgc_n, dgc_onset in list(dgc_pd_onsets_com.items()):

                        # the code in this loop removes the pd onsets that have gap shorter than the
                        # block duration.
                        f_inds = dgc_onset['global_frame_ind']
                        pdo_inds = dgc_onset['global_pd_onset_ind']

                        block_onset_ind = []
                        for i in range(f_inds.shape[0]):
                            if i == 0:
                                block_onset_ind.append(i)
                            else:
                                curr_gap = f_inds[i] - f_inds[block_onset_ind[-1]]
                                if curr_gap > block_frame_num:
                                    block_onset_ind.append(i)

                        # sanity check if number of detected block onsets of each condition
                        # equals the iteration of dgc
                        if len(block_onset_ind) != iteration:
                            raise ValueError('condition "{}": number of the detected block onsets ({}) '
                                             'does not equal iteration of DriftingGratingCircle ({}).'
                                             .format(dgc_n, len(block_onset_ind), iteration))

                        dgc_onset['global_frame_ind'] = f_inds[block_onset_ind]
                        dgc_onset['global_pd_onset_ind'] = pdo_inds[block_onset_ind]

                curr_pd_onsets_com.update(dgc_pd_onsets_com)
            elif stim_n[-38:] == '_StaticGratingCircleRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-31:] == '_StaticImagesRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            elif stim_n[-38:] == '_SinusoidalLuminanceRetinotopicMapping':
                curr_pd_onsets_com.update(self._analyze_pd_onset_combined_general(curr_pd_onsets_seq))
            else:
                raise LookupError('Do not understand stimulus name: {}'.format(stim_n))

            pd_onsets_combined.update({stim_n: curr_pd_onsets_com})

        # print('for debug ...')
        return pd_onsets_combined

    @staticmethod
    def _analyze_pd_onset_combined_general(pd_onsets_sequential):

        pd_onsets_combined = {}

        # get all types of probes
        strs_stim = [po['str_stim'] for po in pd_onsets_sequential]
        strs_stim = set(strs_stim)

        for str_stim in strs_stim:  # for each probe
            pd_onset_list = []
            pd_frame_list = []
            for po in pd_onsets_sequential:
                if po['str_stim'] == str_stim:
                    pd_onset_list.append(po['global_pd_onset_ind'])
                    pd_frame_list.append(po['global_frame_ind'])

            pd_onsets_combined.update({str_stim: {'global_pd_onset_ind': np.array(pd_onset_list),
                                                  'global_frame_ind': np.array(pd_frame_list)}})

        return pd_onsets_combined

    @staticmethod
    def _analyze_pd_onset_combined_locally_sparse_noise(pd_onsets_sequential):

        pd_onsets_combined = {}

        # get all types of probes
        probes = set([])
        for po in pd_onsets_sequential:
            probes = probes | po['strs_stim']

        # print('\n'.join(probes))

        for probe in probes:  # for each probe
            pd_onset_list = []
            pd_frame_list = []
            for po in pd_onsets_sequential:
                if probe in po['strs_stim']:
                    pd_onset_list.append(po['global_pd_onset_ind'])
                    pd_frame_list.append(po['global_frame_ind'])

            pd_onsets_combined.update({probe: {'global_pd_onset_ind': np.array(pd_onset_list),
                                               'global_frame_ind': np.array(pd_frame_list)}})

        return pd_onsets_combined

    @staticmethod
    def _analyze_pd_onset_combined_drifting_grating_circle(pd_onsets_sequential):
        pd_onsets_combined = {}

        # get all types of probes
        strs_stim = [po['str_stim'] for po in pd_onsets_sequential]
        strs_stim = set(strs_stim)

        for str_stim in strs_stim:  # for each probe
            pd_onset_list = []
            pd_frame_list = []
            for po in pd_onsets_sequential:
                if po['str_stim'] == str_stim:
                    pd_onset_list.append(po['global_pd_onset_ind'])
                    pd_frame_list.append(po['global_frame_ind'])

            pd_onsets_combined.update({str_stim: {'global_pd_onset_ind': np.array(pd_onset_list),
                                                  'global_frame_ind': np.array(pd_frame_list)}})

        return pd_onsets_combined

    def _get_dgc_log_dict(self, dgc_name):

        if self.log_dict['stimulation']['stim_name'] == 'CombinedStimuli':
            stim_log = self.log_dict['stimulation']['individual_logs'][dgc_name[:-18]]
        else:
            stim_log = self.log_dict['stimulation']

        return stim_log
