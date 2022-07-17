import time
from enum import IntEnum
import serial.tools.list_ports
from tkinter import messagebox

import pyvisa

ErrorStatusDictionary = {
    100: "Range error. The numeric value sent is not allowed",
    101: "A recall of set up data has been requested but the store specified contains corrupted data",
    102: "A recall of set up data has been requested but the store specified does not contain any data",
    103: "Attempt to read or write a command on the second output when it is not available.",
    104: "Command not valid with output on.",
    200: "Read Only: An attempt has been made to change the settings of the instrument from an interface without "
         "write privileges "
}
"""
This is a Dictionary that contains all the different Error Status Codes that are relevant in the code. 
"""


class TtiPsuChannel(IntEnum):
    """
    This is a class for the enumerations or alias for the different channels of the DC Power Supply.
    """
    Channel_1 = 1
    Channel_2 = 2
    Channel_All = 3


class TtiPsuChannelState(IntEnum):
    """
    This is the state of the channel of the DC Power Supply.
    """
    Off = 0
    On = 1


class TtiPsuOutputMode(IntEnum):
    """
    This is for the output mode of the Power Supply.
    Whether it wants outputs to work independently or for the voltage tracking mode.
    """
    Independent = 2
    Tracking = 0


class TtiPsuLockStatus(IntEnum):
    """
    This is related to the Lock Status of the Power Supply.
    """
    Locked = 1
    Free = 0
    Unavailable = -1


class _OpcReturnState(IntEnum):
    """
    This is for the Return States of the Operation Complete bit in the Standard Event Status Register.
    """
    Success = 1
    NotExecuted = 0


class TtiPsu:
    """
    This is for the initialization of an object of the DC Power Supply.

    """

    def __init__(self, comport):
        try:
            self._ResourceManager = pyvisa.ResourceManager()
            # Please note that we have to find a way to get the COM Port in a less direct way.
            # I am using ASRL4:INSTR for myself but needs to be changed.
            # print([comport.device for comport in serial.tools.list_ports.comports()])
            self._Instrument = self._ResourceManager.open_resource(f'ASRL{comport[3]}::INSTR')
            self._check_execution_reg()  # Checks to make sure the Execution Error Register is clear.

            self.Channel1 = Channel(TtiPsuChannel.Channel_1, self._Instrument)
            self.Channel2 = Channel(TtiPsuChannel.Channel_2, self._Instrument)
        except BaseException:
            raise TtiPsuException("Class init error")

    def __del__(self):
        self._Instrument.close()
        self._ResourceManager.close()

    """
    Private & Diagnostic
    These are private functions that are used for diagnostic purposes. 
    These functions should not be accessed outside of this class.  
    """

    def _opc_status(self) -> _OpcReturnState:
        """
        Query Operation Complete status. The response is always 1<rmt> and will be
        available immediately the command is executed because all commands are
        sequential.

        :return: _OpcReturnState
        """
        query = '*OPC?'

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad instrument respond for query : %s" % query)

        return _OpcReturnState(int(execution_status))

    def _verify_query_result(self, query) -> tuple[None, bool]:
        """
        This function checks and ensures that the query is successful.
        :param query:
        :return: None, bool
        """
        tries = 3
        finished = False
        query_result = None

        while tries and finished is False:
            query_result = self._Instrument.query(query)

            if query_result is not None and len(query_result) > 0:
                finished = True
            else:
                query_result = None

            tries -= 1

        if query_result is None or len(query_result) < 1:
            raise TtiPsuException("Bad instrument respond for query : %s" % query)
        return query_result, finished

    def _query_error_register(self) -> None:
        """
        Query and clear Query Error Register. The response format is nr1<rmt>
        :return: None
        """
        query = 'QER?'

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad instrument respond for query : %s" % query)
        if int(query_result) != 0:
            raise TtiPsuException("Bad instrument respond for query : %s" % query)

    def _check_execution_reg(self) -> None:
        """
        Query and clear Execution Error Register. The response format is nr1<rmt>.
        :return:
        """
        query = 'EER?'

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")
        if int(query_result) != 0 and int(query_result) in ErrorStatusDictionary.keys():
            raise TtiPsuException("Execution error code : %d \n\r Syntax : %s" % int(query_result),
                                  ErrorStatusDictionary[int(query_result)])
        elif int(query_result) != 0 and not int(query_result) in ErrorStatusDictionary.keys():
            raise TtiPsuException("Execution error code : %d \n\r Syntax : Internal Hardware issue" % int(query_result))

    def set_to_local(self) -> None:
        """
        Set device working state from Remote to Local
        Go to local. This does not release any active interface lock so that the lock
        remains with the selected interface when the next remote command is received.
        :return: None
        """

        query = 'LOCAL'

        query_result = self._Instrument.write(query)
        print(f"This function ran and returned {query_result} bytes")
        # if query_result[1] != StatusCode.success: raise TtiPsuException("Query: \r\n" + query + "\r\n didn't
        # execute properly. Status: " + str(query_result[1]))
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_interface_lock(self) -> None:
        """
        Request interface lock. This command requests exclusive access control of the
        instrument. The response is 1 if successful or –1 if the lock is unavailable either
        because it is already in use or the user has disabled this interface from taking
        control using the web interface.

        To avoid error, I would check if the interface is already locked. In that case use the release_lock
        :return: None
        """

        query = 'IFLOCK'

        if self.get_interface_lock() == TtiPsuLockStatus.Unavailable:
            print("This feature is unavailable because the lock status is unavailable")
        elif self.get_interface_lock() == TtiPsuLockStatus.Locked:
            print("The Power Supply is already Locked")
        else:
            query_result = self._Instrument.write(query)

    def get_interface_lock(self) -> TtiPsuLockStatus:
        """
        Returns interface lock status

        Query the status of the interface lock. The return value is 1 if the lock is owned
        by the requesting interfaced instance; 0 if there is no active lock or –1 if the lock
        is unavailable either because it is already in use, or the user has disabled this
        interface from taking control using the web interface.

        :return: TtiPsuLockStatus
        """
        query = 'IFLOCK?'
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        return TtiPsuLockStatus(int(query_result))

    def release_lock(self) -> None:
        """
        Release Interface lock if it's possible

        Release the lock if possible. This command returns the value 0 if successful.
        If this command is unsuccessful –1 is returned, 200 is placed in the Execution
        Register and bit 4 of the Event Status Register is set indicating that there is no
        authority to release the lock.

        :return: None
        """
        query = "IFUNLOCK"

        # query_result = self._Instrument.write(query)
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")
        if int(query_result) != 0:
            raise TtiPsuException("Unable to unlock the device \n\r Query result is : %d" % int(query_result))
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def reset_trip_condition(self) -> None:
        """
        Attempt to clear all TRIP conditions

        :return: None
        """

        query = "TRIPRST"
        query_result = self._Instrument.write(query)
        # if query_result[1] != StatusCode.success: raise TtiPsuException("Query: \r\n" + query + "\r\n didn't
        # execute properly. Status: " + str(query_result[1]))
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_output_all(self, state: TtiPsuChannelState) -> None:
        """
                Set channel state ALL to ON/OFF
        Simultaneously sets all outputs on/off where <nrf> has the following meaning:
        0=ALL OFF, 1=ALL ON.
        If OPALL sets all outputs ON then any that were already on will remain ON
        If OPALL sets all outputs OFF then any that were already off will remain OFF
        :param state: TtiPsuChannelState
        :return: None
        """
        query = 'OPALL %d' % state.value
        query_result = self._Instrument.write(query)
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_operating_mode(self, mode: TtiPsuOutputMode) -> None:
        """
        Set output modes to work in INDEPENDENT mode or TRACKING mode
        :param mode:
        :return: None
        """

        query = "CONFIG %d" % mode.value

        query_result = self._Instrument.write(query)
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def get_operating_mode(self) -> TtiPsuOutputMode:
        """
        Returns current setting of Operating mode
        Reports the operating mode. The response is <nr1><rmt>, where <nr1> is 2 for
        outputs operating independently and 0 for voltage tracking mode.
        :return:
        """

        query = 'CONFIG?'
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        return TtiPsuOutputMode(int(query_result))

    def set_ratio_tracking(self, ratio: int) -> None:
        """
        Change ratio of Slave-Master tracking between <0 - 100> - Works only on previously set TRACKING mode
        Set the ratio of output 2 (slave) to output 1 (master) in tracking mode to <nrf>,
        where <nrf> is the ratio in percent (0 to 100). Ratio can set at any time but will
        not have any effect until voltage tracking mode is set (by using CONFIG <0>).
        :param ratio:
        :return:
        """

        query = "RATIO %d" % ratio

        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def get_ratio(self):
        """
        Returns RATIO setting as float
        Reports the operating mode. The response is <nr1><rmt>, where <nr1> is 2 for
        outputs operating independently and 0 for voltage tracking mode.

        :return:
        """

        query = 'RATIO?'
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        return query_result

    def get_identity(self) -> list:
        """
        Returns device Identity string
        Formatted in a list for easier extraction.
        """

        query = '*IDN?'

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        query_result = query_result.split(",")
        return query_result

    def device_settings_reset(self) -> None:
        """
        Device all REMOTE settings reset
        Resets the instrument to the remote control default settings with the exception of
        all remote interface settings, stored set-ups, Vmin/Vmax values and Output state
        at power-on setting. (see Remote Operation Defaults paragraph in the Remote
        Interface Operation section)
        :return: None
        """

        query = "*RST"

        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def release_limit_lock(self):
        """Clears Status register, Error & Execution Register, And the EVENT Register - responsible for device lock
        Allow user to SOFT-Reset device if error Occurs
        """

        query = "*CLS"
        query_result = self._Instrument.write(query)

        query = "EER?"
        query_result = self._Instrument.write(query)

        query = "LSR%d?" % TtiPsuChannel.Channel_1.value
        query_result = self._Instrument.write(query)

        query = "LSR%d?" % TtiPsuChannel.Channel_2.value
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")
        self._check_execution_reg()


class Channel(TtiPsu):

    def __init__(self, channel, instrument):
        self.channel = channel
        self._Instrument = instrument

    def __del__(self):
        pass

    '''
       Voltage Section :
    '''

    def set_voltage(self, voltage: float, verify: bool = False) -> None:
        """Sets the output voltage on the given channel.

        Switch between standard query set_voltage query and set_voltage with verify
        """

        query = 'V%dV %.3f' % (self.channel.value, voltage) if verify else 'V%d %.3f' % (
            self.channel, voltage)  # Build a query
        query_result = self._Instrument.write(query)
        if self._opc_status() is _OpcReturnState.NotExecuted:  # Check if "Complete bit" is set
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_voltage_trip(self, voltage: float) -> None:
        """Sets over voltage PROTECTION parameter

        User won't be able to set higher voltage -> device lock will be set

        Set output <n> over voltage protection trip point to <nrf> Volts
        """

        query = 'OVP%d %.3f' % (self.channel.value, voltage)
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_voltage_delta(self, voltage: float) -> None:
        """ Change voltage delta parameter on given channel

        Then use set_voltage_inc or set_voltage_dec method
        """

        query = 'DELTAV%d %.3f' % (self.channel.value, voltage)
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_voltage_inc(self, verify: bool = False) -> None:
        """ Allows user to increment voltage by specified delta param

         Swap between standard method and method with verification
        """

        query = 'INCV%dV' % self.channel.value if verify else 'INCV%d' % self.channel.value
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_voltage_dec(self, verify: bool = False) -> None:
        """ Allows user to decrement voltage by specified delta param

        Swap between standard method and method with verification
        """

        query = 'DECV%dV' % self.channel.value if verify else 'DECV%d' % self.channel.value
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_voltage_and_wait(self, value, interval) -> None:
        self.set_voltage(float(value))
        time.sleep(interval)

    def get_voltage(self) -> str:
        """ Returns previously SET voltage value as float """

        query = 'V%d?' % self.channel.value

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")
        query_result = query_result[0:-2].split(" ")

        return query_result

    def get_voltage_trip(self):
        """ Returns previously SET voltage trip setting as float """

        query = 'OVP%d?' % self.channel.value

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")
        return query_result

    def get_voltage_readback(self):
        """ Returns MEASURED voltage value as float """

        query = 'V%dO?' % self.channel.value

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False or not "V" in query_result:
            raise TtiPsuException("Bad respond from instrument")
        return query_result

    def get_voltage_delta(self):
        """ Returns voltage delta setting as float """

        query = 'DELTAV%d?' % self.channel.value

        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False or not "V" in query_result:
            raise TtiPsuException("Bad respond from instrument")

        return query_result  # Device respond is for ex: DELTAV1 <value>

    '''
    Current Section :
    '''

    def set_current(self, current: float):
        """
        Set user desired channel limit on given channel
        :param current:
        :return:
        """

        query = 'I%d %.3f' % (self.channel.value, current)
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_current_trip(self, current: float):
        """
         Set Current Trip PROTECTION value at given channel
        :param current:
        :return:
        """

        query = 'OCP%d %.3f' % (self.channel.value, current)
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_current_delta(self, voltage: float):
        """Set current delta parameter at given channel """

        query = 'DELTAI%d %.3f' % (self.channel.value, voltage)
        query_result = self._Instrument.write(query)
        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_current_inc(self):
        """
        Use previously set delta param to increment channel current limit
        :return:
        """

        query = 'INCI%d' % self.channel.value
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def set_current_dec(self):
        """
        Use previously set delta param to decrement channel current limit
        :return:
        """

        query = 'DECI%d' % self.channel.value
        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def get_current(self) -> float:
        """
        Return current SET at given channel as float
        :return:
        """

        query = 'I%d?' % self.channel.value
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False or "I" not in query_result:
            raise TtiPsuException("Bad respond from instrument")

        return float(query_result[2:-1])

    def get_current_trip(self):
        """
        Return current trip setting as float
        :return:
        """

        query = 'OCP%d?' % self.channel.value
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")
        return query_result

    def get_current_readback(self):
        """
        Return MEASURED current that is already at given channel as float
        """

        query = 'I%dO?' % self.channel.value
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        return query_result

    def get_current_delta(self):
        """
        Return current delta setting at given channel as float
        """

        query = 'DELTAI%d?' % self.channel.value
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False or not "I" in query_result:
            raise TtiPsuException("Bad respond from instrument")

        return query_result

    '''
    Others
    '''

    def set_output_state(self, state: TtiPsuChannelState):
        """
        Set channel state 1/2 to ON/OFF
        set output <n> on/off where <nrf> has the following meaning: 0=OFF, 1=O
        :param state:
        :return:
        """
        query = 'OP%d %d' % (self.channel.value, state.value)

        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def get_output_state(self):
        """
        Return channel state
        Returns output <n> on/off status.
        The response is <nr1><rmt> where 1 = ON, 0 = OFF.
        :return:
        """

        query = 'OP%d?' % self.channel.value
        query_result, execution_status = self._verify_query_result(query)
        if execution_status is False:
            raise TtiPsuException("Bad respond from instrument")

        return TtiPsuChannelState(int(query_result))

    def save_current_config(self, storage_number: int):
        """
        Save the current set-up of output <n> to the set-up store specified by <nrf>
        where <nrf> can be 0-9.
        :param storage_number:
        :return:
        """

        if storage_number > 9 or storage_number < 0:
            raise TtiPsuException("Storage number can not be greater than 9 and lower than 0")

        query = "SAV%d %d" % (self.channel.value, storage_number)

        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")

    def use_saved_config(self, storage_number: int):

        """
        Use previously saved channel output from storage num < 0 - 9 > to given channel
        Recall a set up for output <n> from the set-up store specified by <nrf> where
        <nrf> can be 0-9.
        :param storage_number:
        :return:
        """

        if storage_number > 9 or storage_number < 0:
            raise TtiPsuException("Storage number can not be greater than 9 and lower than 0")

        query = "RCL%d %d" % (self.channel.value, storage_number)

        query_result = self._Instrument.write(query)

        if self._opc_status() is _OpcReturnState.NotExecuted:
            raise TtiPsuException("Device respond for query *OPC? : Return status False")


class TtiPsuException(Exception):

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'TTiPsu Error Message : {0} '.format(self.message)
        else:
            return 'TTiPsu Error Message'
