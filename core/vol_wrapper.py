# vol_wrapper.py - Volatility3 wrapper script
import json
import subprocess
import shutil
import os

class VolatilityManager:
    def __init__(self, dump_path):
        self.dump_path = dump_path
        self.vol_exe = self.get_vol_path()

    def get_vol_path(self):
        # First check if vol.exe is in our virtual environment
        venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "venv", "Scripts", "vol.exe")
        if os.path.exists(venv_path):
            return venv_path
            
        # Then check system path
        system_vol = shutil.which("vol")
        if system_vol:
            return system_vol
            
        # Fallback to default command
        return "vol"

    def run_command(self, plugin_name, extra_args=[]):
        # Run volatility command and return json
        cmd = [self.vol_exe, "-f", self.dump_path, "-r", "json", plugin_name] + extra_args
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"Error running {plugin_name}: {result.stderr}")
                return []
                
            return json.loads(result.stdout)
        except Exception as e:
            print(f"Exception while running {plugin_name}: {e}")
            return []

    def run_pslist(self):
        # Get active processes
        data = self.run_command("windows.pslist.PsList")
        rows = []
        for item in data:
            rows.append([
                str(item.get("PID", "")),
                str(item.get("ImageFileName", item.get("Name", ""))),
                str(item.get("PPID", "")),
                str(item.get("Threads", "")),
                str(item.get("Handles", "")),
                str(item.get("SessionId", item.get("Session", ""))),
                str(item.get("CreateTime", "")),
                str(item.get("ExitTime", ""))
            ])
        return rows

    def run_netscan(self):
        # Get network connections
        data = self.run_command("windows.netscan.NetScan")
        rows = []
        for item in data:
            rows.append([
                str(item.get("Proto", "")),
                str(item.get("LocalAddr", "")),
                str(item.get("LocalPort", "")),
                str(item.get("ForeignAddr", "")),
                str(item.get("ForeignPort", "")),
                str(item.get("State", "")),
                str(item.get("PID", "")),
                str(item.get("Owner", ""))
            ])
        return rows

    def run_malfind(self):
        # Find injected code
        data = self.run_command("windows.malfind.Malfind")
        rows = []
        for item in data:
            rows.append([
                str(item.get("PID", "")),
                str(item.get("Process", item.get("ImageFileName", ""))),
                str(item.get("Start VPN", item.get("StartVpn", ""))),
                str(item.get("End VPN", item.get("EndVpn", ""))),
                str(item.get("Protection", item.get("Tag", ""))),
                str(item.get("Hexdump", item.get("HexDump", "")))[:60],
                str(item.get("Disasm", item.get("Disassembly", "")))[:60]
            ])
        return rows

    def run_hashdump(self):
        # Extract user hashes
        data = self.run_command("windows.hashdump")
        rows = []
        for item in data:
            rows.append([
                str(item.get("User", "")),
                str(item.get("RID", item.get("rid", ""))),
                str(item.get("lmhash", item.get("LMHash", ""))),
                str(item.get("nthash", item.get("NTHash", "")))
            ])
        return rows

    def run_yarascan(self, yara_file):
        # Scan with YARA rules
        data = self.run_command("windows.yarascan.YaraScan", ["--yara-file", yara_file])
        rows = []
        for item in data:
            rows.append([
                str(item.get("Rule", "")),
                str(item.get("PID", item.get("Owner", ""))),
                str(item.get("Process", item.get("ImageFileName", ""))),
                str(item.get("Offset", item.get("offset", ""))),
                str(item.get("Match", item.get("Value", item.get("String", ""))))[:80]
            ])
        return rows
