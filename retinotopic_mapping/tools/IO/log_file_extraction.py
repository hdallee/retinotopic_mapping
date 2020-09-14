import retinotopic_mapping.DisplayLogAnalysis as dla
from pathlib import Path
import os

folder_path = Path("/home/experiment/Experiment/08.01./stimulus/data/visual_display_log/")
file_path = "200801134507-KSstimAllDir-MTest-Name-000-notTriggered-complete.pkl"
full_path = folder_path / file_path

analyser = dla.DisplayLogAnalyzer(full_path)
print("Init ok")
analyser.stim_block_extractor()
print("Stim block extraction done")
analyser.save_to_recording()
