import ctypes
import os
import time
# Get the absolute path to the DLL
dll_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c8855-01api.dll')
print(dll_path)
# Load the DLL
dll = ctypes.WinDLL(dll_path)

# Define the function prototype for connection
dll.C8855Open.argtypes = []
dll.C8855Open.restype = ctypes.c_void_p  # Assuming the handle is a void pointer

# Function to reset the device
dll.C8855Reset.argtypes = [ctypes.c_void_p]
dll.C8855Reset.restype = ctypes.c_bool

def reset_device(handle):
    return dll.C8855Reset(handle)


# Define the function prototype for C8855Setup
dll.C8855Setup.argtypes = [ctypes.c_void_p, ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ushort]
dll.C8855Setup.restype = ctypes.c_bool

# Function to set up the device with a specific gate time and transfer mode
def setup_device(handle, gate_time, transfer_mode, number_of_gate):
    return dll.C8855Setup(handle, gate_time, transfer_mode, number_of_gate)

# Gate time settings
C8855_GATETIME_50US = 0x02
C8855_GATETIME_500US = 0x05
C8855_GATETIME_1MS = 0x06
C8855_GATETIME_10MS = 0x09
C8855_GATETIME_2S = 0x10
C8855_GATETIME_10S = 0x12
# Add other gate time settings as needed

# Transfer mode settings
C8855_SINGLE_TRANSFER = 1
C8855_BLOCK_TRANSFER = 2

# Define the function prototype for C8855CountStart
dll.C8855CountStart.argtypes = [ctypes.c_void_p, ctypes.c_ubyte]
dll.C8855CountStart.restype = ctypes.c_bool
# Trigger mode settings
C8855_SOFTWARE_TRIGGER = 0
C8855_EXTERNAL_TRIGGER = 1
# Function to start the counting process
def start_counting(handle, trigger_mode=C8855_SOFTWARE_TRIGGER):
    return dll.C8855CountStart(handle, trigger_mode)

# Define the function prototype for C8855ReadData
dll.C8855ReadData.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong), ctypes.POINTER(ctypes.c_ubyte)]
dll.C8855ReadData.restype = ctypes.c_bool

# Function to read data from the device

def read_data(handle, data_buffer):
    result_returned = ctypes.c_ubyte()
    success = dll.C8855ReadData(handle, data_buffer, ctypes.byref(result_returned))

    if success:
        print('Data read succeeded.')
        print(f'ResultReturned: {result_returned.value}')
    else:
        print('Data read failed.')

# Define the function prototype for C8855CountStop
dll.C8855CountStop.argtypes = [ctypes.c_void_p]
dll.C8855CountStop.restype = ctypes.c_bool

# Function to stop the counting process
def stop_counting(handle):
    return dll.C8855CountStop(handle)


# Define the function prototype for disconnection
dll.C8855Close.argtypes = [ctypes.c_void_p]
dll.C8855Close.restype = ctypes.c_bool  # The function returns a boolean

# Example usage
# Call the function to connect to the device
device_handle = dll.C8855Open()

# Check if the handle is valid
print(f'Photon counter handle: {device_handle}')

if device_handle:
    success = reset_device(device_handle)
    if success:
        print('C8855Reset succeeded.')
    else:
        print('C8855Reset failed.')
else:
    print('Device handle not obtained. Initialization failed.')


if device_handle:
    success = setup_device(device_handle, gate_time=C8855_GATETIME_1MS, transfer_mode=C8855_BLOCK_TRANSFER, number_of_gate=32)
    if success:
        print('Device setup succeeded.')
    else:
        print('Device setup failed.')
else:
    print('Device handle not obtained. Initialization failed.')


success = start_counting(device_handle)
if success:
    print('Counting started.')
else:
    print('Counting start failed.')

# Wait for the data to be ready
#time.sleep(10.24)  # Wait for 1024 * 10ms = 10.24 seconds

data_buffer = (ctypes.c_ulong * 1024)()
overall_start_time = time.time()
read_data(device_handle, data_buffer)


# Calculate and print the overall elapsed time


success = stop_counting(device_handle)
if success:
    print('Counting stopped.')
else:
    print('Counting stop failed.')


overall_end_time = time.time()
overall_elapsed_time = overall_end_time - overall_start_time
print(f'Overall time taken: {overall_elapsed_time} seconds')
print('Buffer after reading:')
print(data_buffer)
print(list(data_buffer))



success = reset_device(device_handle)
if success:
    print('C8855Reset succeeded.')
else:
    print('C8855Reset failed.')

        
# Call the function to disconnect the device
result = dll.C8855Close(device_handle)
print('closing photon counter')
print(f'counter closed: {result}')


