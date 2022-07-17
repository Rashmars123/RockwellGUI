import pytest
from time import time
from Framework.TtiPsu import *
import pandas as pd
from pathlib import Path
from CSVs import *
from conftest import find_path


class Test_Serial_Interface:
    """
    This is the section of test related to the Digital and Analog Inputs section of the interface
    """

    def test_digital_user_interface(self, fixture_putty_serial):
        """
        This is a test that test whether data is able to be read from batfish
        :param fixture_putty_serial:
        :return:
        """
        loops = 20
        delay_per_cycle = 20
        fixture_putty_serial.digital_user_interface(loops, delay_per_cycle)

        assert find_path('digital.csv').loc[0]['MechanismTripPosition'] == 0

    def test_adc_user_interface(self, fixture_putty_serial):
        """
        This is a test to test the adc component of the hard integration testing
        :param fixture_putty_remote_psu_reset:
        :param fixture_putty_serial:
        :return:
        """
        loops = 20
        delay_per_cycle = 20
        fixture_putty_serial.adc_user_interface(loops, delay_per_cycle)

        assert find_path('adc.csv').loc[3]['R1'] == 3

    def test_switch_user_interface(self, fixture_putty_serial):
        loops = 20
        delay_per_cycle = 20
        fixture_putty_serial.switch_user_interface(loops, delay_per_cycle)
        assert find_path('switch.csv').loc[3]['FlaRange'] == 12

    @pytest.mark.skip
    def test_temp_user_interface(self, fixture_putty_serial):
        raise NotImplementedError

    def test_snapshot_user_interface(self, fixture_putty_serial):
        loops = None
        delay_per_cycle = None
        fixture_putty_serial.snapshot_user_interface()
        assert find_path('snapshot.csv').loc[0][0] == 0

    def test_bucket_user_interface(self, fixture_putty_serial):
        loops = 20
        delay_per_cycle = 20
        fixture_putty_serial.bucket_user_interface(loops, delay_per_cycle)
        assert find_path('bucket.csv').loc[0]["AvgUncompensatedRms"] == 120

    def test_eeprom_user_interface(self, fixture_putty_serial):
        fixture_putty_serial.eeprom_user_interface()
        assert find_path('eeprom.csv').loc[0]['Value'] == 12288

    def test_version_user_interface(self, fixture_putty_serial):
        fixture_putty_serial.version_user_interface()
        assert find_path('version.csv').loc[0][0] == '0.7.7 Series 0'

    def test_stack_user_interface(self, fixture_putty_serial):
        fixture_putty_serial.stack_user_interface()
        assert find_path('stack.csv').loc[0][2] == "0 of 8192"

    def test_rng_user_interface(self, fixture_putty_serial):
        loops = 20
        delay_per_cycle = 20
        fixture_putty_serial.rng_user_interface(loops, delay_per_cycle)
        assert find_path('rng.csv').loc[0][3] == "<0...1>"
