import inspect
import time

import pytest

from Framework.TtiPsu import *
from Framework.cDaq import cDaq
import serial
from Framework.HIT_Putty_Interface import *
import pandas as pd
from datetime import datetime
from Tests.test_serialinterface import Test_Serial_Interface
from os import listdir
from os.path import isfile, join
import serial.tools.list_ports
import inspect
from conftest import *
from Tests.test_serialinterface import *


# pytest.cmdline.main(['Tests\\test_serialinterface.py::Test_Serial_Interface::test_digital_batfish'])

# startTime = datetime.now()
# hit = HIT_Interface()
# lst = hit.adc_user_interface()
# lst1 = hit.digital_user_interface()
# lst2, message2 = hit.stack_user_interface()
# lst3 = hit.switch_user_interface()
# lst4, title = hit.snapshot_user_interface()
# lst5 = hit.version_user_interface()
# lst6, message3 = hit.eeprom_user_interface()
# lst7, message = hit.rng_user_interface()
# lst8 = hit.bucket_user_interface()
# t = (lst, lst1, lst2, lst3, lst4, lst5, lst6, lst7, lst8)
# for x in t:
#     print(x)
#     if x == {} or "":
#         print("This is an error")
# print(datetime.now() - startTime)

# onlyfiles = [f for f in listdir('CSVs') if isfile(join('CSVs', f))]

cDAQ1 = cDaq()
cDAQ1.ConfigOutputs()

cDAQ1.cDaqTask.write([False, False, True, False,
                      True, False, True, False,
                      False, False, True, False,
                      True, False, True, False])


#  cDAQ2 = cDaq()
#  cDAQ2.ConfigInputs()
# print(cDAQ2.cDaqTask.read(number_of_samples_per_channel=1))
# print(cDAQ1.cDaqTask.do_channels.channel_names)
# cDAQ1.cDaqTask.write([True, False, True, False, True, False, True, False, False, False, True, False, True, False, True, False])
# cDAQ1.cDaqTask.write([False, False, True, False, True, False, True, False, False, False, True, False, True, False, True, False])
# cDAQ1.cDaqTask.write([True, False, True, False, True, False, True, False, False, False, True, False, True, False, True, False])

""