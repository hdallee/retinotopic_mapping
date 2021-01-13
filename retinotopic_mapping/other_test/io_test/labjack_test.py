from visexpa.engine.datahandlers.labjack import U3Wrap
from visexpa.engine.datahandlers.labjack import test_read, test_write_pulses
import time

with U3Wrap() as jack:
    print(jack.check_voltage_range())
    jack.jack.setDIOState(0, state=1)
    print(jack.jack.getDIState(1))
    time.sleep(1)
    jack.jack.setDIOState(0, state=0)
    print(jack.jack.getDIState(1))
    time.sleep(1)
# test_read()
# test_write_pulses()