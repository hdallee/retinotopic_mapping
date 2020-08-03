import retinotopic_mapping.DisplayLogAnalysis as dla
import os

folder_path = "/home/abel/PycharmProjects/Stimulus_gen/retinotopic_mapping/retinotopic_mapping/examples/visual_stimlation/C:/data/visual_display_log/"
file_path = "200731150039-DriftingGratingCircle-MTest-Name-000-notTriggered-complete.pkl"
full_path = folder_path + file_path

analyser = dla.DisplayLogAnalyzer(full_path)
print("Init ok")
log_dict = analyser.get_stim_dict()
print("done")
analyser.stim_block_extractor()
