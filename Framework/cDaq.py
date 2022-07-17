from enum import IntEnum
import nidaqmx
from nidaqmx.constants import TerminalConfiguration


class ChannelOutputsEnum(IntEnum):
    CH0 = 1,
    CH1 = 2,
    CH2 = 4,
    CH3 = 8,
    CH4 = 16,
    CH5 = 32,
    CH6 = 64,


class cDaq:

    def __init__(self):
        self.cDaqTask = nidaqmx.Task()

    def __del__(self):
        self.cDaqTask.close()

    def ConfigOutputs(self):
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line0')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line1')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line2')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line3')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line4')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line5')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line6')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod2/port0/line7')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line0')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line1')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line2')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line3')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line4')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line5')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line6')
        self.cDaqTask.do_channels.add_do_chan('cDAQ1Mod3/port0/line7')
        self.cDaqTask.start()

    def ConfigInputs(self):
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai0', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai1', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai2', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai3', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai4', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai5', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai6', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.ai_channels.add_ai_voltage_chan('cDAQ1Mod1/ai7', terminal_config=TerminalConfiguration.RSE)
        self.cDaqTask.start()


    # # read-modify-write function for disabling the serial output relays
    # def DisableCircuits(self, outputs: int):
    #     tmp, rel = self.ReadVal()
    #     tmp = tmp & (~outputs)
    #     self.WriteVal(tmp, rel)
    #
    # # read-modify-write function for enabling the serial output relays
    # def EnableCircuits(self, outputs: int):
    #     tmp, rel = self.ReadVal()
    #     tmp = tmp | outputs
    #     self.WriteVal(tmp, rel)
