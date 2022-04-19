import retinotopic_mapping.DisplayLogAnalysis as dla
from pathlib import Path
import os

def save_log_to_recording(filepath: str, script_source: str):
    """
    Extract the stimulus parameters needed for analysis from a single .pkl log file, and save them
    to the corresponding .hdf5 recording file.

    Parameters
    ----------
    filepath : str
        Full path to the file.

    Returns
    -------
    None
    """
    analyser = dla.DisplayLogAnalyzer(Path(filepath))
    analyser.stim_block_extractor()
    analyser.save_to_recording(recording_full_path=None, script_source=script_source)


def save_logs_in_folder_to_recording(folder_path: Path, filter=None):
    """
    Extract the stimulus parameters needed for analysis from the .pkl log files in a folder, and save them
    to their corresponding .hdf5 recording files.

    Parameters
    ----------
    folder_path: Path
    Path of the folder which contains the log files.

    """
    for filename in os.listdir(folder_path):
        print(filename)
        if filter and not filter in filename:  # Only analyse files the name of which contain the filter string
            continue
        if filename[-3:] == 'pkl':
            analyser = dla.DisplayLogAnalyzer(folder_path / filename, skip_integrity_check=True)
            print("Init ok")
            analyser.stim_block_extractor()
            print("Stim block extraction done")
            analyser.save_to_recording()


def save_logs_in_folder_to_json(folder_path: Path):
    """
    Extract the stimulus parameters needed for analysis from the .pkl log files in a folder, and save them
    to .json files.

    Parameters
    ----------
    folder_path: Path
    Path of the folder which contains the log files.

    """
    for filename in os.listdir(folder_path):
        print(filename)
        if filename[-3:] == 'pkl':
            analyser = dla.DisplayLogAnalyzer(folder_path / filename)
            print("Init ok")
            analyser.stim_block_extractor()
            print("Stim block extraction done")
            analyser.save_to_json()

if __name__ == '__main__':
    # folder_path = Path("D:/Widefield experiment data/12.18/N.o. 35/good_cp/stimulus/data/visual_display_log/")
    folder_path = Path("/media/hillierlab/T7/Data/Experiment/2021/11.19_Cirmi_widefield/stimulus/visual_display_log/")
    save_logs_in_folder_to_recording(folder_path, filter="1213")
    exit()
    file_path = "201028113056-CombinedStimuli-MTest-Name-000-notTriggered-complete.pkl"
    full_path = folder_path / file_path
    an = dla.DisplayLogAnalyzer(full_path)
    print("OKOK")

