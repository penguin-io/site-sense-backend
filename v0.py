#v0.py sets up the normal rtsp stream
#for this it injects the following lines of code(without the comments)into /root/jaefar/mtx/mediamtx.yml
"""
(after the line which begins with,without the double quotes and no indentation, "paths:", where indentation matters)
convert_{cli parameter cid}_v0:
    source: rtsp://localhost:8554/v0/{cid}
    sourceOnDemand: yes
"""
import argparse

def update_config(cid):
    config_path = "/root/jaefar/mtx/mediamtx.yml"
    new_entry = f"    convert_{cid}_v0:\n        source: rtsp://localhost:8554/v0/{cid}\n        sourceOnDemand: yes\n"
    
    with open(config_path, "r") as file:
        lines = file.readlines()
    
    updated_lines = []
    paths_found = False
    inserted = False
    
    for line in lines:
        updated_lines.append(line)
        if line.strip() == "paths:":
            paths_found = True
        elif paths_found and not inserted and line.strip() == "all_others:":
            updated_lines.insert(-1, new_entry)
            inserted = True
    
    if not paths_found:
        raise ValueError("Could not find 'paths:' in the configuration file.")
    if not inserted:
        raise ValueError("Could not insert before 'all_others:' in the configuration file.")
    
    with open(config_path, "w") as file:
        file.writelines(updated_lines)

def main():
    parser = argparse.ArgumentParser(description="Update mediamtx.yml with a new RTSP path.")
    parser.add_argument("--cid", required=True, help="Client ID")
    parser.add_argument("--r_url", required=True, help="RTSP input URL")
    
    args = parser.parse_args()
    update_config(args.cid)

if __name__ == "__main__":
    main()

