import os
import glob
try:
    from Evtx.Evtx import Evtx
    from Evtx.Views import evtx_file_xml_view
except ImportError:
    raise ImportError("python-evtx not installed. Please add it to your container.")

LOG_DIR = "/log"

def convert_evtx_files():
    evtx_files = glob.glob(os.path.join(LOG_DIR, "*.evtx"))
    for evtx_file in evtx_files:
        out_file = evtx_file + ".txt"
        try:
            with Evtx(evtx_file) as log:
                xml_str = ''.join(str(item[0]) if isinstance(item, tuple) else str(item) for item in evtx_file_xml_view(log))
                with open(out_file, "w") as f_out:
                    f_out.write(f"Parsed events from {os.path.basename(evtx_file)}:\n")
                    f_out.write(xml_str)
        except Exception as e:
            print(f"Error converting {evtx_file}: {e}")

if __name__ == "__main__":
    convert_evtx_files()
    print("EVTX conversion complete.")
