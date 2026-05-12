# yara_scanner.py - YARA scanning module
import os
import glob
import shutil
import urllib.request
from core.vol_wrapper import VolatilityManager

# Check if yara module is installed
try:
    import yara
    HAS_YARA = True
except ImportError:
    HAS_YARA = False

class YaraScanner:
    def __init__(self):
        # Create yara_rules folder if it doesn't exist
        self.rules_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yara_rules")
        if not os.path.exists(self.rules_folder):
            os.makedirs(self.rules_folder)
            
        # URLs for standard rules
        self.urls = {
            "gen_suspicious_strings.yar": "https://raw.githubusercontent.com/Neo23x0/signature-base/master/yara/gen_suspicious_strings.yar",
            "apt_cobaltstrike.yar": "https://raw.githubusercontent.com/Neo23x0/signature-base/master/yara/apt_cobaltstrike.yar",
            "gen_mimikatz.yar": "https://raw.githubusercontent.com/Neo23x0/signature-base/master/yara/gen_mimikatz.yar"
        }

    def add_custom_rule(self, source):
        """Validate and add a custom YARA rule from a local path or URL."""
        temp_file = None
        
        try:
            # Check if source is a URL
            if source.startswith("http://") or source.startswith("https://"):
                # Download to a temp file
                filename = source.split("/")[-1].split("?")[0]
                if not filename.endswith((".yar", ".yara")):
                    filename = "custom_downloaded.yar"
                temp_file = os.path.join(self.rules_folder, f"_temp_{filename}")
                try:
                    urllib.request.urlretrieve(source, temp_file)
                except Exception as e:
                    raise ValueError(f"Download failed for URL:\n{source}\n\nError: {e}")
                local_path = temp_file
            else:
                # Local file
                if not os.path.exists(source):
                    raise ValueError(f"File not found:\n{source}")
                local_path = source
                filename = os.path.basename(source)
            
            # Validate with yara-python if available
            if HAS_YARA:
                try:
                    yara.compile(filepath=local_path)
                except yara.SyntaxError as e:
                    raise ValueError(f"YARA Syntax Error in '{filename}':\n{e}")
                except Exception as e:
                    raise ValueError(f"Failed to compile '{filename}':\n{e}")
            
            # Copy/move to rules folder with final name
            dest = os.path.join(self.rules_folder, filename)
            if temp_file and os.path.exists(temp_file):
                # Rename temp file to final name
                if os.path.exists(dest):
                    os.remove(dest)
                os.rename(temp_file, dest)
                temp_file = None  # Prevent cleanup since we renamed it
            else:
                shutil.copy(local_path, dest)
            
            return dest
            
        finally:
            # Cleanup temp file if something went wrong
            if temp_file and os.path.exists(temp_file):
                os.remove(temp_file)

    def download_missing_rules(self):
        # Download rules from internet
        for filename, link in self.urls.items():
            file_path = os.path.join(self.rules_folder, filename)
            if not os.path.exists(file_path):
                try:
                    urllib.request.urlretrieve(link, file_path)
                except Exception as e:
                    print(f"Could not download {filename}: {e}")

    def merge_all_rules(self):
        # Combine all .yar files into one file called all_rules.yar
        all_files = glob.glob(os.path.join(self.rules_folder, "*.yar"))
        merged_file = os.path.join(self.rules_folder, "all_rules.yar")
        
        # Files to skip during merge
        skip_names = {"all_rules.yar", "_merged_rules.yar"}
        
        with open(merged_file, "w", encoding="utf-8") as out_file:
            for filepath in all_files:
                # Skip generated/merged files
                basename = os.path.basename(filepath)
                if basename in skip_names:
                    continue
                    
                # Test the rule with yara-python if available
                if HAS_YARA:
                    try:
                        yara.compile(filepath=filepath)
                    except:
                        print(f"Skipping broken rule file: {filepath}")
                        continue
                        
                # Add file content with proper newlines
                content = open(filepath, "r", encoding="utf-8", errors="ignore").read()
                out_file.write(f"\n// File: {basename}\n")
                out_file.write(content)
                out_file.write("\n")
                
        return merged_file

    def auto_scan(self, dump_path):
        # Do all steps automatically
        self.download_missing_rules()
        merged_file = self.merge_all_rules()
        
        # Run volatility
        vol = VolatilityManager(dump_path)
        return vol.run_yarascan(merged_file)

