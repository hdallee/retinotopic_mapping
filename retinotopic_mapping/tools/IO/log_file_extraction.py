import retinotopic_mapping.DisplayLogAnalysis as dla
import os

folder_path = "/home/experiment/Experiment_data/"
file_path = "200804152128-CombinedStimuli-MTest-Name-000-notTriggered-complete.pkl"
full_path = folder_path + file_path

analyser = dla.DisplayLogAnalyzer(full_path)
print("Init ok")
analyser.stim_block_extractor()
print("done")
