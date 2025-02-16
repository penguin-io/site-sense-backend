import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(
        description="Initialize multiple processes with given arguments."
    )
    parser.add_argument("--cid", required=True, help="Client ID")
    parser.add_argument("--r_url", required=True, help="RTSP URL")
    args = parser.parse_args()

    scripts = ["v0.py", "v1.py", "v2.py", "v3.py"]

    for script in scripts:
        cmd = ["python3", script, "--cid", args.cid, "--r_url", args.r_url]
        subprocess.Popen(cmd)


if __name__ == "__main__":
    main()
