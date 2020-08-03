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


def extract_dir_order_of_iteration(frame_directions, shown_directions):
    """
    Extract grating direction order of one iteration of a drifting grating stimulus log.
    :param frame_directions: List of the stimulus direction of every frame.
    :param shown_directions: List of the directions that were shown.
    :return:
    """

    first_appearance_ind_list = []
    for j in shown_directions:
        index = first_index_finder(frame_directions, j)
        first_appearance_ind_list.append(index)
    # sorted_indices holds the indices corresponding to the directions in all_dirs sorted by their first appearance
    sorted_indices = heapq.nsmallest(8, range(len(first_appearance_ind_list)), key=first_appearance_ind_list.__getitem__)

    print(first_appearance_ind_list)
    # print(sorted_indices)
    dirs_inorder = []
    for k in sorted_indices:
        dirs_inorder.append(shown_directions[k])
    print(dirs_inorder)

    # The last direction shown in the iteration is: all_dirs[sorted_indices[-1]]
    # We search for the last frame where a direction was shown in the iteration
    last_frame_of_first_iteration = last_index_finder(frame_directions, shown_directions[sorted_indices[-1]]) + 1
    # print(count_occurence(dir_list, all_dirs[sorted_indices[-1]]))
    return first_appearance_ind_list, last_frame_of_first_iteration