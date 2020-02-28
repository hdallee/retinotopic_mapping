from visexpA.engine.datahandlers.labjack import U3Wrap
from visexpA.engine.datahandlers.labjack import test_read, test_write_pulses

with U3Wrap() as jack:
    print(jack.check_voltage_range())
    jack.jack.setDIOState(0, state=1)
    print(jack.jack.getDIState(1))
    jack.jack.setDIOState(0, state=0)
    print(jack.jack.getDIState(1))
# test_read()
# test_write_pulses()