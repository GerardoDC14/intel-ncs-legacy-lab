import sys
from openvino.runtime import Core, get_version
core = Core()
print('Python:', sys.version.split()[0])
print('OpenVINO:', get_version())
devices = core.available_devices
print('Devices:', devices)
assert any(d.startswith('MYRIAD') for d in devices), 'MYRIAD plugin unavailable'
print('MYRIAD plugin enumerated; USB hardware and inference not verified.')
