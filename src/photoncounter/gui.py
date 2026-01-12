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
from spcs_instruments import C8855_counting_unit
from spcs_instruments.spcs_instruments_utils import load_config
import toml
from pathlib import Path

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
number_of_bins = None
gate_time_label = None
gate_time = None
counts = 0
counter = None
style = tb.Style()
theme_path = Path(__file__).parent / "theme.json"
style.load_user_themes(theme_path)
style.theme_use("gruvbox")
master = style.master
gate_time_to_byte = {
    "50us": 0x02,
    "100us": 0x03,
    "200us": 0x04,
    "500us": 0x05,
    "1ms": 0x06,
    "2ms": 0x07,
    "5ms": 0x08,
    "10ms": 0x09,
    "20ms": 0x0A,
    "50ms": 0x0B,
    "100ms": 0x0C,
    "200ms": 0x0D,
    "500ms": 0x0E,
    "1s": 0x0F,
    "2s": 0x10,
    "5s": 0x11,
    "10s": 0x12,
}

pane = tk.Frame(master)
pane.grid(row=0, column=0, padx=10, pady=5)
pane2 = tk.Frame(master)
pane2.grid(row=0, column=1, padx=10, pady=5)
master.iconbitmap(Path(__file__).parent / "lightbulb.ico")
master.title("C8855 Photon Counter")
gatetime_label = tb.Label(
    pane,
    text="Gate time:",
).grid(row=1, column=0, padx=5, pady=5)


config = load_config(Path(__file__).parent / "config.toml")


def setup_plot():
    plt.style.use("dark_background")
    fig = Figure(figsize=(4, 4), dpi=200)
    ax = fig.add_subplot(111)
    ax.clear
    ax.set_facecolor("#282828")
    x_to_plot = np.arange(1024)
    y_to_plot = np.zeros(1024)
    ax.set_xlabel("Time")
    ax.set_ylabel("Counts")
    ax.xaxis.label.set_color("#ebdbb2")
    ax.yaxis.label.set_color("#ebdbb2")
    ax.set_xlim(0, 150)  # Cover the range of x_to_plot
    ax.set_ylim(0, 10)  # Cover the potential range of y_to_plot
    fig.tight_layout()
    (line,) = ax.plot(x_to_plot, y_to_plot, color="#b8bb26")
    fig.patch.set_facecolor("#282828")
    ax.tick_params(color="#ebdbb2", labelcolor="#ebdbb2")
    for spine in ax.spines.values():
        spine.set_edgecolor("#ebdbb2")
    return fig, ax, line, y_to_plot, x_to_plot


def number_of_bins_dropdown(e):
    global number_of_bins

    if scan.running == True:
        pass
    else:
        number_of_bins = int(number_of_bins_select.get())


def gatetime_dropdown(e):
    global gate_time
    global gate_byte_value
    if scan.running == True:
        pass
    else:
        gate_time = gatetime_dropdown_select.get()


def transfer_dropdown(e):
    global transfer_type
    global trans_byte_value
    if scan.running == True:
        pass
    else:
        transfer_type = transfer_dropdown_select.get()


def trigger_dropdown(e):
    global trigger_type
    global trigger_byte_value
    if scan.running == True:
        pass
    else:
        trigger_type = trigger_dropdown_select.get()


def start():
    if scan.running == True:
        pass
    else:
        global interupt_type
        global x_to_plot
        global y_to_plot
        global counts
        global start_time
        global counter

        config["device"]["C8855_photon_counter"]["gate_time"] = (
            gatetime_dropdown_select.get()
        )
        config["device"]["C8855_photon_counter"]["transfer_type"] = (
            transfer_dropdown_select.get()
        )
        config["device"]["C8855_photon_counter"]["trigger_type"] = (
            trigger_dropdown_select.get()
        )
        config["device"]["C8855_photon_counter"]["number_of_gates"] = int(
            number_of_bins_select.get()
        )
        with open("config.toml", "w") as f:
            toml.dump(config, f)
        counter = counter = C8855_counting_unit("config.toml", connect_to_pyfex=False)
        if interupt_type == "stop" or interupt_type == "finished":
            y_to_plot = []
            x_to_plot = []
            if not scan.running:
                scan.running = True
                start_time = str(datetime.datetime.now())
                scan()
        elif interupt_type == "pause":
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
        interupt_type = "stop"
        init_graph = "yes"
        scan.running = False


def scan():
    global interupt_type
    global gate_byte_value
    global trans_byte_value
    global iterator
    global init_graph
    global y_to_plot
    global x_to_plot
    global number_of_bins
    global counts
    global counter
    if scan.running == True:
        data_buffer, counts = counter.measure()
        time.sleep(1)

        alpha = "".join(filter(str.isalpha, gate_time))
        nums = "".join(filter(str.isdigit, gate_time))

        y_to_plot = data_buffer

        max_x = int(nums) * (number_of_bins - 1)
        x_to_plot = np.arange(0, int(number_of_bins_select.get())) * int(nums)

        ax.set_xlim(0, max_x)
        ax.set_xlabel("Time (" + alpha + ")")

        update_plot()
        scan.i += 1
        iterator += 1
        master.after(10, scan)

    elif scan.running == False and interupt_type == "stop":
        iterator = 0
        scan.i = 0

    else:
        global stop_time
        scan.running = False
        interupt_type = "finished"
        init_graph = "yes"
        print("measurement finished")
        stop_time = str(datetime.datetime.now())
        iterator = 0
        scan.i = 0


def update_plot():
    global x_to_plot, y_to_plot, ax, line, number_of_bins, counts

    line.set_xdata(x_to_plot)
    line.set_ydata(y_to_plot)
    type(y_to_plot)
    print(y_to_plot)
    counts_var.set(str(counts))

    ax.set_ylim(
        min(y_to_plot[0 : int(number_of_bins)]),
        max(y_to_plot[0 : int(number_of_bins)] + 10),
    )

    # Redraw the plot
    ax.figure.canvas.draw()
    counts = counts


counts_var = tk.StringVar()
counts_var.set("0")

gate_times = list(gate_time_to_byte.keys())
gatetime_dropdown_select = tb.Combobox(pane, values=gate_times)
gatetime_dropdown_select.grid(row=1, column=1, padx=5, pady=5)
gatetime_dropdown_select.bind("<<ComboboxSelected>>", gatetime_dropdown)


transfer_label = tb.Label(
    pane,
    text="Transfer Type:",
).grid(row=2, column=0, padx=5, pady=5)

transfer_type_to_bytes = {
    "Block (recomended)": "block_transfer",
    "Single": "single_transfer",
}
transfer_types = list(transfer_type_to_bytes.values())
transfer_dropdown_select = tb.Combobox(pane, values=transfer_types)
transfer_dropdown_select.grid(row=2, column=1, padx=5, pady=5)
transfer_dropdown_select.bind("<<ComboboxSelected>>", transfer_dropdown)

trigger_label = tb.Label(
    pane,
    text="Trigger:",
).grid(row=3, column=0, padx=5, pady=5)
trigger_type_to_byte = {"Internal (software)": "software", "External": "external"}
trigger_types = list(trigger_type_to_byte.values())
trigger_dropdown_select = tb.Combobox(pane, values=trigger_types)
trigger_dropdown_select.grid(row=3, column=1, padx=5, pady=5)
trigger_dropdown_select.bind("<<ComboboxSelected>>", trigger_dropdown)


number_of_bins_label = tb.Label(
    pane,
    text="Number of bins",
).grid(row=4, column=0, padx=5, pady=5)
bins_list = [32, 64, 128, 256, 512]
number_of_bins_select = tb.Combobox(pane, values=bins_list)
number_of_bins_select.grid(row=4, column=1, padx=5, pady=5)
number_of_bins_select.bind("<<ComboboxSelected>>", number_of_bins_dropdown)


start_scan = tb.Button(pane, text="Start Measure", command=start).grid(
    row=9, column=0, padx=5, pady=5
)
stop_scan = tb.Button(pane, text="Stop Measure", command=stop).grid(
    row=9, column=1, padx=5, pady=5
)

counts_label = tb.Label(
    pane,
    text="Counts:",
).grid(row=10, column=0, padx=5, pady=5)
current_counts = tb.Label(
    pane,
    textvariable=counts_var,
).grid(row=10, column=1, padx=5, pady=5)
fig, ax, line, y_to_plot, x_to_plot = setup_plot()
canvas = FigureCanvasTkAgg(fig, master=pane2)
canvas.draw()
canvas.get_tk_widget().grid(row=7, column=1)
phase = 0
scan.i = 0
scan.running = False


def run_app():
    master.mainloop()


if __name__ == "__main__":
    run_app()
