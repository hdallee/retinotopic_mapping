"""
This script is a template for preparing recording scripts for your experiments.
"""
from visexpa.engine.datahandlers.teledyne_camera import record

animal_id = 'Rat_no57'
comment = ''  # Eg: laser_power_50 or not_dark_adapted etc.

if __name__ == '__main__':
    record("from_file", length=30, comment=animal_id + '_' + comment)
