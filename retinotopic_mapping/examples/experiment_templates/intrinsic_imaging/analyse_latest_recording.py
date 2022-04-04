import os
import glob
from pathlib import Path
from visexpa.engine.dataprocessors.widefield_analysis_protocols import widefield_analysis_in_folder

if __name__ == '__main__':
    os.chdir("data")
    list_of_recordings = glob.glob("*.hdf5")
    latest_recording = max(list_of_recordings, key=os.path.getctime)
    print(latest_recording)

    folder_path = Path(os.getcwd())

    widefield_analysis_in_folder(folder_path, downscale=4, filter=latest_recording)
