import time
import pytest
from Framework.TtiPsu import *


def blinked_light(fixture_cdaq, Channel: str) -> bool:
    """
    This is a function for finding out if a light is blinking.
    :param fixture_cdaq:
    :param Channel: Which channel are you look at
    :return: A Boolean value of whether the light is blinking or not
    """
    start_time = time.time()
    seconds = 2
    lst = [-1]
    count = 0  # count the amount of times the data changes
    blinked = False
    while True:
        current_time = time.time()
        elapsed_time = current_time - start_time

        prev = lst.pop()
        # this is going to store the data
        data = fixture_cdaq.cDaqTask.read(number_of_samples_per_channel=1)[Channel][0]
        if data != prev:
            if prev == -1:
                pass
            elif (data > 1) and (prev > 1):
                pass  # power spike
            elif (data < 1) and (prev < 1):
                pass  # off
            else:
                count += 1
        if count == 2:
            blinked = True
            count = 0
        lst.append(data)

        if elapsed_time > seconds:
            break

    return blinked


@pytest.mark.cdaq
@pytest.mark.remote_psu
class Test_Sample_Tests:

    @pytest.mark.parametrize("volts", [0.50, 1.00, 1.50, 2.00, 2.50, 3.00, 3.50, 4.00, 4.50, 5.00, 4.33])
    def test_analog_read_accuracy(self, fixture_cdaq, fixture_remote_psu_reset, volts):
        fixture_remote_psu_reset.Channel2.set_voltage(volts)
        assert float(fixture_remote_psu_reset.Channel2.get_voltage()[1]) == volts
        exp_volt = fixture_remote_psu_reset.Channel2.get_voltage()
        fixture_cdaq.ConfigInputs()
        data = fixture_cdaq.ReadVal()[0]
        print(data)

        assert round(data, 2) == float(exp_volt[1])

    def test_digital_output(self, fixture_cdaq):
        fixture_cdaq.ConfigOutputs()
        data = fixture_cdaq.cDaqTask.write([True, True, True, True, True, False, False, False, True, True, True, True, True, False, False, False])
        assert data == 1

    @pytest.mark.skip
    def test_blinking_light(self, fixture_remote_power_supply_cycle_power, fixture_cdaq):
        """
        This is a test that tests whether the light is blinking
        :param fixture_remote_power_supply_cycle_power:
        :param fixture_cdaq:
        :return:
        """
        fixture_cdaq.ConfigInputs()

        assert blinked_light(fixture_cdaq, 0)

    @pytest.mark.skip
    def test_not_blinking_light(self, fixture_remote_psu_reset, fixture_cdaq):
        """
        This is a test that test if the light is not blinking
        :param fixture_remote_psu_reset:
        :param fixture_cdaq:
        :return:
        """
        fixture_cdaq.ConfigInputs()

        assert not blinked_light(fixture_cdaq, 0)

    @pytest.mark.skip
    def test_safety(self, fixture_remote_power_supply_cycle_power, fixture_cdaq):
        """
        This test is supposed to do the following things:
        Turn on Power of 24VDC
        Delay 5 Seconds
        Set the FLA Dial Position to 5
        Turn on Load Current(Level TBD)
        Turn on the Product (Energize the Digital Input of the DAQ card)
        Delay(X Seconds TBD)
        Is the light blinking RED (1 time)
        Check that the fault relay is not tripped
        Press the Reset Button (Assert the digital output)
        Turn off Power (0VDC)
        Delay 5 Seconds
        :param fixture_remote_power_supply_cycle_power:
        :param fixture_cdaq:
        :return:
        """
        # fixture_cdaq.ConfigOutputs()
        # # Set FLA Dial Position 5 & Load Current (Implement a while loop)
        # fixture_cdaq.cDaqTask.write(True)  # Depending on how it is configured this will set Dial Position to 5
        # time.sleep(5)  # This is to be determined...
        #
        # fixture_cdaq.ConfigInputs()
        #
        # # Depending on how it configured we will read the light in the specific channel
        # if blinked_light(fixture_cdaq, 0):
        #     # This means that the light blinking Red is tripped
        #     # Check fault relay is not tripped
        #     fixture_cdaq.cDaqTask.read()  # More details to come regards in how it is configured
        #     # Press the Reset Button
        #     fixture_cdaq.cDaqTask.write(True)  # More details to come in terms of how everything is configured

