import sys
from pathlib import Path
from spcs_instruments.spcs_instruments_utils import load_config
import toml

def configure_photoncounter():

    if len(sys.argv) != 2:
        print("Usage: python script.py <path_to_dll>")
        sys.exit(1)
    
    dll_path = sys.argv[1]
    config = {
    "device": {
        "C8855_photon_counter": {
            "dll_path": dll_path,
            "gate_time": "",
            "averages": 1,
            "transfer_type": "",
            "trigger_type": "",
            "number_of_gates": "",
            "measure_mode": "all"
        }
    }
}    
    print(f"saving config to {Path(__file__).parent}")   
    print(f" writing dll path: {dll_path}")
    with open(Path(__file__).parent / "config.toml", "w") as f:
                toml.dump(config, f)