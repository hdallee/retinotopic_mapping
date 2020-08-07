import pickle
import heapq
import numpy as np
import os


def first_index_finder(list, dir):
    """
    Finds and returns the index of the first frame in list where the stimulus direction was dir.
    :param list: The list which holds the direction values of every displayed frame.
    :param dir: The direction we are looking for.
    :return: The index of the first occurrence of dir in list.
    """
    for x in enumerate(list):
        if x[1] == dir:
            return x[0]


def last_index_finder(list, dir):
    """
    Finds and returns the index of the first frame where that frame is followed by gap.
    :param list: The list which holds the direction values of every displayed frame.
    :param dir: The direction we are looking for.
    :return: The index of the first last occurrence of dir in list.
    """
    for x in range(len(list)):
        if list[x] == dir and list[x+1]==None:
            return x


def extract_dir_order_of_iteration(dir_list, all_dirs, num_iterations):

    first_appearance_ind_list = []
    for j in all_dirs:
        index = first_index_finder(dir_list, j)
        first_appearance_ind_list.append(index)
    # sorted_indices holds the indices corresponding to the directions in all_dirs sorted by their first appearance
    sorted_indices = heapq.nsmallest(8, range(len(first_appearance_ind_list)), key=first_appearance_ind_list.__getitem__)

    print(first_appearance_ind_list)
    # print(sorted_indices)
    dirs_inorder = []
    for k in sorted_indices:
        dirs_inorder.append(all_dirs[k])
    print(dirs_inorder)
    # print((data['presentation']['displayed_frames'][100][4]))

    # for l in data['presentation']['displayed_frames']:
    # The last direction shown in the iteration is: all_dirs[sorted_indices[-1]]
    # We search for the last frame where a direction was shown in the iteration
    # print(last_index_finder(dir_list,all_dirs[sorted_indices[-1]]))
    last_frame_of_first_iteration = last_index_finder(dir_list, all_dirs[sorted_indices[-1]]) + 1
    # print(count_occurence(dir_list, all_dirs[sorted_indices[-1]]))
    # print(dir_list[2460])
    return first_appearance_ind_list, last_frame_of_first_iteration

def write_parameters_to_file(fhandler, pkl_data):
    fhandler.write(f"Number of iterations: {pkl_data['stimulation']['iteration']}\n")
    fhandler.write(f"Pregap duration: {pkl_data['stimulation']['pregap_dur']}\n")
    fhandler.write(f"Postgap duration: {pkl_data['stimulation']['postgap_dur']}\n")
    fhandler.write(f"Midgap duration: {pkl_data['stimulation']['midgap_dur']}\n")
    fhandler.write(f"Block duration: {pkl_data['stimulation']['block_dur']}\n")
    fhandler.write(f"Refresh rate (fps): {pkl_data['monitor']['refresh_rate']}\n")


path_to_file = r'/home/abel/abel/TTK/Data_stim_gep/visual_display_log/200603/'

all_dirs = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]

for filename in os.listdir(path_to_file):
    if filename.endswith(".pkl") and "incomplete" not in filename:
        print(filename)

        with open(os.path.join(path_to_file, filename), 'rb') as f:
            data = pickle.load(f)
            # print(data)
            num_iterations = data['stimulation']['iteration']
            # dir_list holds the direction parameter of every displayed frame
            dir_list = []
            for i in data['presentation']['displayed_frames']:
                dir_list.append(i[4])

        print(f"Number of iterations: {num_iterations}")

        out_filename = filename[:12] + ".txt"
        out_file_full_path = os.path.join(path_to_file, out_filename)

        with open(out_file_full_path, 'w') as outfile:

            write_parameters_to_file(outfile, data)
            outfile.write("\nDirections and frame indices\n")
            for item in all_dirs:
                outfile.write(str(item) + ", ")
            outfile.write("\n")

            # The number of frames cut from the beginning of dir_list
            num_of_cut_frames = 0
            for i in range(num_iterations):
                first_appearance_ind_list, last_frame_of_iteration = extract_dir_order_of_iteration(dir_list, all_dirs, num_iterations)
                dir_list = dir_list[last_frame_of_iteration:]

                first_appearance_ind_list = list(np.asarray(first_appearance_ind_list) + num_of_cut_frames)
                num_of_cut_frames += last_frame_of_iteration
                for item in first_appearance_ind_list:
                    outfile.write(str(item) + ", ")
                outfile.write("\n")
