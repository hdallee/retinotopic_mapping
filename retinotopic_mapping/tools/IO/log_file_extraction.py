import retinotopic_mapping.DisplayLogAnalysis as dla
from pathlib import Path
import os


def save_logs_in_folder_to_recording(folder_path=None):
    for filename in os.listdir(folder_path):
        print(filename)
        if filename[-3:] == 'pkl':
            analyser = dla.DisplayLogAnalyzer(folder_path / filename)
            print("Init ok")
            analyser.stim_block_extractor()
            print("Stim block extraction done")
            analyser.save_to_recording()


if __name__ == '__main__':
    folder_path = Path("D:/Widefield experiment data/12.18/N.o. 35/good_cp/stimulus/data/visual_display_log/")
    save_logs_in_folder_to_recording(folder_path)
    exit()
    file_path = "201028113056-CombinedStimuli-MTest-Name-000-notTriggered-complete.pkl"
    full_path = folder_path / file_path
    an = dla.DisplayLogAnalyzer(full_path)
    print("OKOK")

