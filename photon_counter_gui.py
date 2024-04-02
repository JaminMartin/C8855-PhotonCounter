# Importing tkinter module
import tkinter as tk
import numpy as np 
import ttkbootstrap as tb
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from ttkbootstrap.constants import *
from time import sleep
import time
import datetime

from C8855_01_driver_wrapper import open_device, reset_device, setup_device, start_counting, stop_counting, close_device, read_data
import ctypes
"""
Def Plot
"""
plt.style.use('dark_background')
fig = Figure(figsize=(4, 4), dpi = 200)
ax = fig.add_subplot(111)
ax.clear
ax.set_facecolor('#282a36')
x_to_plot = np.arange(1024)
y_to_plot = np.zeros(1024)
ax.set_xlabel('Time')
ax.set_ylabel('Counts')
ax.xaxis.label.set_color('#ffb86c')
ax.yaxis.label.set_color('#ffb86c')
ax.set_xlim(0, 1024)  # Cover the range of x_to_plot
ax.set_ylim(0, 10)  # Cover the potential range of y_to_plot
fig.tight_layout()
line, = ax.plot(x_to_plot, y_to_plot, color = '#bd93f9')
fig.patch.set_facecolor('#282a36')
ax.tick_params(color='#ffb86c', labelcolor='#ffb86c')
for spine in ax.spines.values():
        spine.set_edgecolor('#ffb86c')

"""
globals
"""

gate_time = None
transfer_type = None
emulation_status = False

iterator = 0 
y_to_plot = []
x_to_plot = []
interupt_type = None
start_time = None
stop_time = None
init_graph = None
gate_byte_value = None
trans_byte_value = None
trigger_byte_value = None


   

def gatetime_dropdown(e):
    global gate_time
    global gate_byte_value
    if scan.running == True: 
        pass 
    else:
        gate_time = gatetime_dropdown_select.get()

        gate_byte_value = gate_time_to_byte[gate_time]
       

def transfer_dropdown(e):
    global transfer_type
    global trans_byte_value
    if scan.running == True: 
        pass 
    else:
    
        transfer_type = transfer_dropdown_select.get()
        
        trans_byte_value = transfer_type_to_bytes[transfer_type]

def trigger_dropdown(e):
    global trigger_type
    global trigger_byte_value
    if scan.running == True: 
        pass 
    else:
        trigger_type = trigger_dropdown_select.get()
        
        trigger_byte_value = trigger_type_to_byte[trigger_type]


def start():
        if scan.running == True: 
            pass 
        else:
            global interupt_type 
            global x_to_plot
            global y_to_plot 
            global counts 
            global start_time
         
            # if counter.emulation == True and interupt_type != 'pause':
            #     counts = np.zeros(1024)
            # else: 
            #     counts = np.zeros(1024)
            if interupt_type == 'stop' or interupt_type == 'finished':
                y_to_plot = []
                x_to_plot = []
                if not scan.running:
                    scan.running = True
                    start_time = str(datetime.datetime.now())
                    scan()
            elif interupt_type == 'pause':
                if not scan.running:     
                    scan.running = True
                    scan()   
            else:    
                if not scan.running:
                    scan.running = True
                    start_time = str(datetime.datetime.now())
                    scan()
        

def stop():
    if scan.running == False: 
        pass 
    else:
        global interupt_type
        global stop_time
        global init_graph
        interupt_type = 'stop'
        init_graph = 'yes'
        scan.running = False 




def scan():
    global interupt_type
    global gate_byte_value
    global trans_byte_value
    global iterator
    global init_graph
    global y_to_plot
    global x_to_plot
    if scan.running == True:
    
        device_handle = open_device()
        
    # Check if the handle is valid
        print(f'Photon counter handle: {device_handle}')
        

        if device_handle:
            success = reset_device(device_handle)
            if success:
                print('C8855Reset succeeded.')
            else:
                print('C8855Reset failed.')
                scan.running = False
        else:
            print('Device handle not obtained. Initialization failed.')
            scan.running = False

        if device_handle:
            success = setup_device(device_handle, gate_time=gate_byte_value, transfer_mode=trans_byte_value, number_of_gate=512)
            if success:
                print('Device setup succeeded.')
            else:
                print('Device setup failed.')
                scan.running = False
        else:
            print('Device handle not obtained. Initialization failed.')
            scan.running = False

        success = start_counting(device_handle, trigger_mode= trigger_byte_value)
        if success:
            print('Counting started.')
        else:
            print('Counting start failed.')
            scan.running = False

        data_buffer = (ctypes.c_ulong * 1024)()
       
        read_data(device_handle, data_buffer)  

        success = stop_counting(device_handle)
        if success:
            print('Counting stopped.')
        else:
            print('Counting stop failed.')
            scan.running = False
        time.sleep(1)    
        y_to_plot = np.asarray(list(data_buffer))
        x_to_plot = np.arange(0,1024)




        update_plot()
        scan.i += 1
        iterator += 1
        master.after(10, scan)  


    elif scan.running == False and interupt_type == 'stop':
        print('Scan stopped saving data regardless...')
        iterator = 0
        scan.i = 0
   

    else:
        global stop_time
        scan.running = False 
        interupt_type = 'finished'
        init_graph = 'yes'
        print('measurement finished')
        stop_time = str(datetime.datetime.now())
        iterator = 0
        scan.i = 0



def update_plot():
    global x_to_plot, y_to_plot, ax, line

    # Update line data
    line.set_xdata(x_to_plot)
    line.set_ydata(y_to_plot)
  
    # Rescale the axes to fit the updated data
    ax.set_ylim(min(y_to_plot), max(y_to_plot + 10))

    # Redraw the plot
    ax.figure.canvas.draw()
    counts = np.sum(y_to_plot)
    counts_var.set(counts)




style = tb.Style()
style.load_user_themes('theme.json')
style.theme_use('dracula')
master = style.master


pane = tk.Frame(master)
pane.grid(row=0, column=0, padx=10, pady=5)
pane2 = tk.Frame(master)
pane2.grid(row=0, column=1, padx=10, pady=5)

gatetime_label = tb.Label(pane,text='Gate time:',).grid(row=1, column=0, padx=5, pady=5)
gate_time_to_byte = {
    '50us': 0x02,
    '100us': 0x03,
    '200us': 0x04,
    '500us': 0x05,
    '1ms': 0x06,
    '2ms': 0x07,
    '5ms': 0x08,
    '10ms': 0x09,
    '20ms': 0x0A,
    '50ms': 0x0B,
    '100ms': 0x0C,
    '200ms': 0x0D,
    '500ms': 0x0E,
    '1s': 0x0F,
    '2s': 0x10,
    '5s': 0x11,
    '10s': 0x12,
}


counts_var = tk.StringVar()  
counts_var.set('0')

gate_times = list(gate_time_to_byte.keys())
gatetime_dropdown_select = tb.Combobox(pane, values = gate_times)
gatetime_dropdown_select.grid(row=1, column=1,padx=5, pady=5)
gatetime_dropdown_select.bind("<<ComboboxSelected>>", gatetime_dropdown)


transfer_label = tb.Label(pane,text='Transfer Type:',).grid(row=2, column=0, padx=5, pady=5)

transfer_type_to_bytes = {'Block (recomended)': 2, 'Single': 1}
transfer_types = list(transfer_type_to_bytes.keys())
transfer_dropdown_select = tb.Combobox(pane, values = transfer_types)
transfer_dropdown_select.grid(row=2, column=1,padx=5, pady=5)
transfer_dropdown_select.bind("<<ComboboxSelected>>", transfer_dropdown)

trigger_label = tb.Label(pane,text='Trigger:',).grid(row=3, column=0, padx=5, pady=5)
trigger_type_to_byte = {'Internal (software)': 0, 'External': 1}
trigger_types = list(trigger_type_to_byte.keys())
trigger_dropdown_select = tb.Combobox(pane, values = trigger_types)
trigger_dropdown_select.grid(row=3, column=1,padx=5, pady=5)
trigger_dropdown_select.bind("<<ComboboxSelected>>", trigger_dropdown)


start_scan = tb.Button(pane, text='Start Measure',command = start ).grid(row=9, column=0, padx=5, pady=5)
stop_scan = tb.Button(pane, text='Stop Measure',command = stop).grid(row=9, column=1, padx=5, pady=5)

counts_label = tb.Label(pane, text='Counts:',).grid(row=10, column=0, padx=5, pady=5)
current_counts = tb.Label(pane,textvariable=counts_var,).grid(row=10, column=1, padx=5, pady=5)

canvas = FigureCanvasTkAgg(fig, master=pane2)
canvas.draw()
canvas.get_tk_widget().grid(row =7,column=1)
phase = 0
# Execute Tkinter
scan.i = 0  
scan.running = False   


 
master.mainloop()


