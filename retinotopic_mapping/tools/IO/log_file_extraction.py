import retinotopic_mapping.DisplayLogAnalysis as dla
from pathlib import Path
import os


def save_logs_in_folder_to_recording(folder_path=None):
    for filename in os.listdir(folder_path):
        if filename[-3:] == 'pkl':
            analyser = dla.DisplayLogAnalyzer(folder_path / filename)
            print("Init ok")
            analyser.stim_block_extractor()
            print("Stim block extraction done")
            analyser.save_to_recording()


if __name__ == '__main__':
    folder_path = Path("/media/experiment/5CECA892ECA867CA/Data/Experiment/10.20/stimulus/data/visual_display_log/")
    save_logs_in_folder_to_recording(folder_path)
    # file_path = "201020150925-CombinedStimuli-MTest-Name-000-notTriggered-complete.pkl"
    # full_path = folder_path / file_path
