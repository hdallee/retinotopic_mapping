import pickle
import heapq

def first_index_finder(list, dir):
    ind = 0
    for x in list:
        if x == dir:
            return ind
        ind = ind+1

def last_index_finder(list, dir):
    for x in range(len(list)):
        if list[x] == dir and list[x+1]==None:
            return x

def count_occurence(list, dir):
    count = 0
    for x in list:
        if x == dir:
            count += 1
    return count

def extract_dir_order_of_iteration(dir_list, all_dirs):

    first_appearance_ind_list = []
    for j in all_dirs:
        index = first_index_finder(dir_list, j)
        first_appearance_ind_list.append(index)
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
    return last_frame_of_first_iteration

path_to_file = r'/home/abel/Egyetem/FOT/FOT_clean/retinotopic_mapping-Git_master/retinotopic_mapping/examples/visual_stimlation/C:/data/visual_display_log/'
file_name = '200116155917-DriftingGratingCircle-MTest-Name-000-notTriggered-complete.pkl'
file_full_path = path_to_file+file_name

all_dirs = [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0]
# we extract num iterations later from the file
num_iterations = 0


with open(file_full_path, 'rb') as f:
    data = pickle.load(f)
    # print(data)
    num_iterations = data['stimulation']['iteration']
    dir_list = []
    for i in data['presentation']['displayed_frames']:
        dir_list.append(i[4])

print(f"Number of iterations: {num_iterations}")

for i in range(num_iterations):
    last_frame_of_iteration = extract_dir_order_of_iteration(dir_list, all_dirs)
    dir_list = dir_list[last_frame_of_iteration:]
    print(dir_list[0])
