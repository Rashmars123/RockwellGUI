import pytest

from Framework.TtiPsu import *
from Framework.cDaq import cDaq
import time
import serial
from Framework.HIT_Putty_Interface import *
import pandas as pd

"""
This is the configuration file for py.test.
It also contains setup and teardown fixtures as well
as common functions 
"""


def find_path(datafile):
    path = Path(datafile)
    absPath = str(path.parent.absolute())
    dirPath = '\\'.join(absPath.split('\\')[0:-1])
    relPath = f'{dirPath}\\CSVs\\{datafile}'
    try:
        df = pd.read_csv(relPath)
    except FileNotFoundError as e:
        relPath = f'{dirPath}\\Rasheedattempt\\CSVs\\{datafile}'
        df = pd.read_csv(relPath)
    return df


pytest_plugins = 'pytest_session2file'


@pytest.fixture(scope="session", autouse=False)
def remote_power_supply_connection():
    """
    This initiates a connection once per session to the remote power supply, used by the fixture_remote_power_supply
    """

    # Setup
    # Read the setup-specific configuration

    # Create the Power Supply Unit (PSU) object
    # so that we can control the class A and B supply.
    # The COM4 serial port is being used for communication.

    remote_psu = TtiPsu(comport='COM4')

    yield remote_psu

    # Teardown
    # None


# This ensures that the Tti PSU is on at the beginning of every session and at the correct voltage.
# This should only be false for developer testing purposes.
@pytest.fixture(scope="session", autouse=False)
def fixture_remote_power_supply(remote_power_supply_connection):
    """
    Fixture to be used in tests that provide the ability to remotely control a power supply
    """
    remote_psu = remote_power_supply_connection

    # Set the Class A voltage to 24.0V
    remote_psu.Channel1.set_voltage(24.0)

    # Set the Class B voltage to 24.0V
    remote_psu.Channel2.set_voltage(24.0)

    # Turn both power supply channels on at the same time.
    remote_psu.set_output_all(TtiPsuChannelState.On)

    # Wait a little so that hardware can initialize
    time.sleep(5)

    yield remote_psu

    # Leave it on at 24.0V in case of other tests don't need remote power supply

    # Set the Class A voltage to 24.0V
    remote_psu.Channel1.set_voltage(24.0)

    # Set the Class B voltage to 24.0V
    remote_psu.Channel2.set_voltage(24.0)
    remote_psu.set_output_all(TtiPsuChannelState.On)


# Fixture for supply voltage restore, in order to prevent other tests from failing when a test, that is updating the
# supply voltage, unexpectedly fails
@pytest.fixture(scope="module", autouse=False)
def fixture_remote_power_supply_restore_voltage(fixture_remote_power_supply):
    ClassAInitialVoltage = fixture_remote_power_supply.Channel1.get_voltage()
    ClassBInitialVoltage = fixture_remote_power_supply.Channel2.get_voltage()
    yield fixture_remote_power_supply
    fixture_remote_power_supply.Channel1.set_voltage(ClassAInitialVoltage)
    fixture_remote_power_supply.Channel2.set_voltage(ClassBInitialVoltage)


@pytest.fixture(scope="session", autouse=False)
def fixture_remote_power_supply_cycle_power(remote_power_supply_connection):
    remote_psu = remote_power_supply_connection

    # Turn Class A and B power supply back on
    remote_psu.Channel1.set_voltage(24.0)
    remote_psu.Channel2.set_voltage(24.0)
    remote_psu.set_output_all(TtiPsuChannelState.On)

    time.sleep(5)

    yield remote_psu

    # Turn off the power supply, without switching the PSU internal relay.
    remote_psu.Channel1.set_voltage(0.0)
    remote_psu.Channel2.set_voltage(0.0)
    remote_psu.set_output_all(TtiPsuChannelState.On)

    # Wait a little so that the supply voltage falls to zero and the target device resets
    time.sleep(5)


@pytest.fixture(autouse=False)
def fixture_remote_psu_reset(remote_power_supply_connection):
    remote_psu = remote_power_supply_connection
    remote_psu.Channel1.set_voltage(0)
    remote_psu.Channel1.set_voltage(0)
    remote_psu.set_output_all(TtiPsuChannelState.On)
    time.sleep(5)

    yield remote_psu

    remote_psu.Channel1.set_voltage(24)
    remote_psu.Channel1.set_voltage(24)
    remote_psu.set_output_all(TtiPsuChannelState.On)
    time.sleep(5)


@pytest.fixture()
def fixture_cdaq():
    """
        Creates connection to NI cDAQ
    """

    CDAQ = cDaq()

    yield CDAQ


@pytest.fixture(scope='session')
def fixture_putty_serial():
    ser = HIT_Interface(comport_psu='COM4', comport_hit="COM5")

    yield ser

    ser.__del__()


@pytest.fixture(autouse=False, scope="function")
def fixture_putty_remote_psu_reset(remote_power_supply_connection):
    remote_psu = remote_power_supply_connection
    remote_psu.Channel1.set_voltage(0)
    remote_psu.Channel1.set_current(0)
    remote_psu.set_output_all(TtiPsuChannelState.On)
    time.sleep(2)

    remote_psu.Channel1.set_voltage(24)
    remote_psu.Channel1.set_current(.1)
    remote_psu.set_output_all(TtiPsuChannelState.On)
    time.sleep(2)

    yield remote_psu
