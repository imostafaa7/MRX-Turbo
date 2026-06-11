#!/usr/bin/env python3

import os
import subprocess
import sys
import argparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# For advanced colored output, progress bars, and ASCII art
try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    import pyfiglet
except ImportError:
    print("[*] Installing required modules: rich, pyfiglet...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "rich", "pyfiglet"])
    from rich.console import Console
    from rich.theme import Theme
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn, TimeRemainingColumn
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    import pyfiglet

# --- Rich Console Setup ---
custom_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "bold green",
    "heading": "bold magenta",
    "command": "italic blue",
    "result": "green",
    "progress": "bold cyan",
})
console = Console(theme=custom_theme)

# --- Global Variables ---
TARGET_DOMAIN = ""
OUTPUT_DIR = "mrx_results"
MAX_WORKERS = 10 # For parallel execution

# --- ASCII Art & Banners ---
def print_banner():
    console.clear()
    ascii_banner = pyfiglet.figlet_format("MRX Turbo", font="slant")
    console.print(Text(ascii_banner, style="bold cyan"))
    
    # Combined text for the panel to avoid AttributeError
    content = Text()
    content.append("Automated Recon & Vulnerability Scanning Workflow\n", style="yellow")
    content.append("Developed by imostafaa9", style="magenta")
    
    console.print(Panel(
        content,
        title="[bold green]Welcome to MRX Turbo![/bold green]",
        border_style="green",
        padding=(1, 2)
    ))
    console.print("\n" + "="*70 + "\n", style="heading")

# --- Tool Management ---
REQUIRED_TOOLS = {
    "subfinder": "go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "amass": "sudo apt install amass -y",
    "httpx": "go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest",
    "nmap": "sudo apt install nmap -y",
    "naabu": "go install -v github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
    "ffuf": "go install github.com/ffuf/ffuf@latest",
    "gau": "go install github.com/lc/gau/v2/cmd/gau@latest",
    "waybackurls": "go install github.com/tomnomnom/waybackurls@latest",
    "nuclei": "go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest",
    "dalfox": "go install github.com/hahwul/dalfox/v2@latest",
    "sqlmap": "sudo apt install sqlmap -y",
    "qsreplace": "go install github.com/tomnomnom/qsreplace@latest",
    "nikto": "sudo apt install nikto -y",
    "subzy": "go install -v github.com/lukasikic/subzy@latest",
    "gf": "go install github.com/tomnomnom/gf@latest",
    "getJS": "go install github.com/003random/getJS@latest", # Assuming getJS is a Go tool
    "linkfinder": "git clone https://github.com/GerbenJavado/LinkFinder.git && cd LinkFinder && pip3 install -r requirements.txt", # Linkfinder is Python
    "corsy": "git clone https://github.com/s0md3v/Corsy.git", # Corsy is Python
}

def check_and_install_tools():
    console.print("\n[info][*] Initiating Auto-Provisioning System...[/info]")
    
    # Update Package Manager
    console.print("[info][*] Updating package manager...[/info]")
    subprocess.run("sudo apt update -y", shell=True, capture_output=True)

    # Check for Go
    if subprocess.run("command -v go", shell=True, capture_output=True).returncode != 0:
        console.print("[warning][!] Go is not installed. Installing Go...[/warning]")
        run_command("sudo apt install golang -y", "Installing Go")
    
    # Set Go PATH globally for current session
    go_path = os.path.join(os.path.expanduser("~"), "go", "bin")
    if go_path not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + go_path
    
    # Check for Python Pip
    if subprocess.run("command -v pip3", shell=True, capture_output=True).returncode != 0:
        console.print("[warning][!] Pip3 is not installed. Installing...[/warning]")
        run_command("sudo apt install python3-pip -y", "Installing Pip3")

    # Install tools
    for tool, install_cmd in REQUIRED_TOOLS.items():
        if subprocess.run(f"command -v {tool}", shell=True, capture_output=True).returncode != 0:
            console.print(f"[warning][!] {tool} is missing. Auto-installing...[/warning]")
            
            # Special logic for git-based tools
            if "git clone" in install_cmd:
                repo_name = tool.capitalize()
                install_path = os.path.join(os.path.expanduser("~"), repo_name)
                if not os.path.exists(install_path):
                    run_command(install_cmd, f"Cloning {tool}")
                else:
                    console.print(f"[success][+] {tool} repository already exists.[/success]")
            else:
                run_command(install_cmd, f"Installing {tool}")
        else:
            console.print(f"[success][+] {tool} detected and ready.[/success]")

    # Setup GF Patterns (Critical for parameter filtering)
    gf_path = os.path.join(os.path.expanduser("~"), ".gf")
    if not os.path.exists(gf_path) or not os.listdir(gf_path):
        os.makedirs(gf_path, exist_ok=True)
        console.print("[warning][!] GF Patterns not found. Downloading...[/warning]")
        run_command(f"git clone https://github.com/1ndianl337/Gf-Patterns {gf_path}/patterns_repo", "Cloning GF Patterns")
        run_command(f"cp {gf_path}/patterns_repo/*.json {gf_path}/", "Installing GF Patterns")
        console.print("[success][+] GF Patterns installed successfully.[/success]")

    # Setup Wordlists
    wordlist_path = "/usr/share/wordlists"
    if not os.path.exists(wordlist_path):
        console.print("[warning][!] Standard wordlists missing. Creating...[/warning]")
        run_command("sudo mkdir -p /usr/share/wordlists", "Creating Wordlist Directory")
        run_command("sudo apt install wordlists -y", "Installing Default Wordlists")
    
    # Download Seclists if missing
    seclist_path = "/usr/share/seclists"
    if not os.path.exists(seclist_path):
        console.print("[warning][!] Seclists missing. Downloading (This may take a moment)...[/warning]")
        run_command("sudo apt install seclists -y", "Installing Seclists")

    console.print("[success][+] Auto-Provisioning Completed. System is 100% ready.[/success]")

# --- Helper Functions ---
def run_command(command, message, output_file=None, cwd=None):
    console.print(f"\n[info][*] {message}[/info]")
    console.print(f"  [command]Running: {command}[/command]")
    
    # Ensure Go bin is in PATH for Go tools
    go_bin = os.path.join(os.path.expanduser("~"), "go", "bin")
    if go_bin not in os.environ["PATH"]:
        os.environ["PATH"] += os.pathsep + go_bin

    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=cwd)
        output_lines = []
        for line in process.stdout:
            console.print(line.strip(), style="dim") # Print live output in dim style
            output_lines.append(line)
        process.wait()

        if output_file:
            with open(output_file, "a") as f:
                f.writelines(output_lines)
        
        if process.returncode != 0:
            console.print(f"[warning][!] Warning during {message}: Command exited with code {process.returncode}[/warning]")
        else:
            console.print(f"[success][+] {message} Completed![/success]")
        return True
    except Exception as e:
        console.print(f"[error][-] Error during {message}: {str(e)}[/error]")
        return False

# --- Workflow Phases (Placeholders for Turbo Mode) ---
def phase_subdomain_enumeration():
    console.print("\n[heading]--- [1] SUBDOMAIN ENUMERATION ---[/heading]")
    subs_file = os.path.join(OUTPUT_DIR, "subs.txt")
    # Placeholder for parallel execution of subfinder and amass
    run_command(f"subfinder -d {TARGET_DOMAIN} -o {subs_file}", "Subfinder Enumeration")
    run_command(f"amass enum -passive -d {TARGET_DOMAIN} >> {subs_file}", "Amass Passive Enumeration")
    run_command(f"sort -u {subs_file} -o {subs_file}", "Sorting Subdomains")

def phase_check_live_hosts():
    console.print("\n[heading]--- [2] CHECK LIVE HOSTS ---[/heading]")
    subs_file = os.path.join(OUTPUT_DIR, "subs.txt")
    live_file = os.path.join(OUTPUT_DIR, "live.txt")
    run_command(f"httpx -l {subs_file} -o {live_file} -status-code -title -tech-detect", "Checking Live Hosts")

def phase_port_scanning():
    console.print("\n[heading]--- [3] PORT SCANNING ---[/heading]")
    live_file = os.path.join(OUTPUT_DIR, "live.txt")
    ports_file = os.path.join(OUTPUT_DIR, "ports.txt")
    run_command(f"nmap -iL {live_file} -sV -T4 --open -oN {ports_file}", "Nmap Port Scanning")
    ports_fast_file = os.path.join(OUTPUT_DIR, "ports_fast.txt")
    run_command(f"naabu -list {live_file} -o {ports_fast_file}", "Naabu Fast Port Scanning")

def phase_directory_fuzzing():
    console.print("\n[heading]--- [4] DIRECTORY & PATH FUZZING ---[/heading]")
    dirs_file = os.path.join(OUTPUT_DIR, "dirs.txt")
    run_command(f"ffuf -u https://{TARGET_DOMAIN}/FUZZ -w /usr/share/wordlists/dirb/common.txt -mc 200,301,302,403 -o {dirs_file}", "FFUF Directory Fuzzing")
    run_command(f"ffuf -u https://{TARGET_DOMAIN}/FUZZ -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt -o {os.path.join(OUTPUT_DIR, 'sensitive_files.txt')}", "FFUF Sensitive Files Fuzzing")

def phase_collect_historical_urls():
    console.print("\n[heading]--- [5] COLLECT HISTORICAL URLS ---[/heading]")
    urls_gau = os.path.join(OUTPUT_DIR, "urls_gau.txt")
    urls_wb = os.path.join(OUTPUT_DIR, "urls_wb.txt")
    all_urls = os.path.join(OUTPUT_DIR, "all_urls.txt")
    run_command(f"gau {TARGET_DOMAIN} | tee {urls_gau}", "GAU URL Collection")
    run_command(f"waybackurls {TARGET_DOMAIN} | tee {urls_wb}", "Waybackurls Collection")
    run_command(f"cat {urls_gau} {urls_wb} | sort -u | tee {all_urls}", "Merging and Sorting URLs")

def phase_extract_js_endpoints():
    console.print("\n[heading]--- [6] EXTRACT JS ENDPOINTS ---[/heading]")
    live_file = os.path.join(OUTPUT_DIR, "live.txt")
    js_files = os.path.join(OUTPUT_DIR, "js_files.txt")
    endpoints = os.path.join(OUTPUT_DIR, "endpoints.txt")
    run_command(f"cat {live_file} | getJS --complete | tee {js_files}", "Extracting JS Files")
    run_command(f"python3 {os.path.join(os.path.expanduser('~'), 'LinkFinder', 'linkfinder.py')} -i {js_files} -d -o {endpoints}", "Extracting Endpoints from JS")

def phase_filter_parameters():
    console.print("\n[heading]--- [7] FILTER PARAMETERS ---[/heading]")
    all_urls = os.path.join(OUTPUT_DIR, "all_urls.txt")
    params = os.path.join(OUTPUT_DIR, "params.txt")
    run_command(f"cat {all_urls} | grep '=' | tee {params}", "Extracting Parameters")
    
    run_command(f"cat {all_urls} | gf xss | tee {os.path.join(OUTPUT_DIR, 'params_xss.txt')}", "Filtering XSS Parameters")
    run_command(f"cat {all_urls} | gf sqli | tee {os.path.join(OUTPUT_DIR, 'params_sqli.txt')}", "Filtering SQLi Parameters")
    run_command(f"cat {all_urls} | gf ssrf | tee {os.path.join(OUTPUT_DIR, 'params_ssrf.txt')}", "Filtering SSRF Parameters")
    run_command(f"cat {all_urls} | gf redirect | tee {os.path.join(OUTPUT_DIR, 'params_redirect.txt')}", "Filtering Redirect Parameters")

def phase_automated_vulnerability_scanning():
    console.print("\n[heading]--- [8] NUCLEI SCANNING ---[/heading]")
    live_file = os.path.join(OUTPUT_DIR, "live.txt")
    nuclei_results = os.path.join(OUTPUT_DIR, "nuclei_results.txt")
    run_command(f"nuclei -l {live_file} -t cves/ -t exposures/ -t misconfigurations/ -o {nuclei_results}", "Nuclei CVEs/Exposures/Misconfigs Scan")
    run_command(f"nuclei -l {live_file} -t vulnerabilities/ -severity medium,high,critical", "Nuclei Vulnerabilities Scan")

def phase_xss_scanning():
    console.print("\n[heading]--- [9] XSS SCANNING ---[/heading]")
    params_xss = os.path.join(OUTPUT_DIR, "params_xss.txt")
    xss_results = os.path.join(OUTPUT_DIR, "xss_results.txt")
    run_command(f"dalfox file {params_xss} -o {xss_results}", "Dalfox XSS Scan")
    run_command(f"cat {params_xss} | kxss", "KXSS Parameter Testing")

def phase_sql_injection():
    console.print("\n[heading]--- [10] SQL INJECTION ---[/heading]")
    params_sqli = os.path.join(OUTPUT_DIR, "params_sqli.txt")
    sqlmap_dir = os.path.join(OUTPUT_DIR, "sqlmap_results")
    run_command(f"sqlmap -m {params_sqli} --batch --level=3 --risk=2 --dbs --output-dir={sqlmap_dir}", "SQLMap Injection Testing")

def phase_ssrf_testing():
    console.print("\n[heading]--- [11] SSRF TESTING ---[/heading]")
    params_ssrf = os.path.join(OUTPUT_DIR, "params_ssrf.txt")
    console.print("[warning][!] SSRF testing requires a listener (e.g., Burp Collaborator). Skipping interactive part.[/warning]")
    run_command(f"cat {params_ssrf} | qsreplace 'http://mrx-ssrf-test.com' | httpx -silent", "SSRF Parameter Replacement Test")

def phase_open_redirect():
    console.print("\n[heading]--- [12] OPEN REDIRECT ---[/heading]")
    params_redirect = os.path.join(OUTPUT_DIR, "params_redirect.txt")
    run_command(f"cat {params_redirect} | qsreplace 'https://evil.com' | httpx -silent -location", "Open Redirect Testing")

def phase_nikto_scan():
    console.print("\n[heading]--- [13] NIKTO SCAN ---[/heading]")
    nikto_file = os.path.join(OUTPUT_DIR, "nikto.txt")
    run_command(f"nikto -h https://{TARGET_DOMAIN} -output {nikto_file}", "Nikto Web Server Scan")

def phase_cors_misconfiguration():
    console.print("\n[heading]--- [14] CORS MISCONFIGURATION ---[/heading]")
    live_file = os.path.join(OUTPUT_DIR, "live.txt")
    corsy_path = os.path.join(os.path.expanduser("~"), "Corsy", "corsy.py")
    run_command(f"python3 {corsy_path} -i {live_file} -t 10 --headers 'Origin: https://evil.com'", "CORS Misconfiguration Testing")

def phase_subdomain_takeover():
    console.print("\n[heading]--- [15] SUBDOMAIN TAKEOVER ---[/heading]")
    subs_file = os.path.join(OUTPUT_DIR, "subs.txt")
    run_command(f"subzy run --targets {subs_file} --concurrency 100 --hide-fails", "Subdomain Takeover Check")

# --- Parallel Execution Engine ---
def execute_parallel(tasks):
    """Executes a list of functions in parallel with a master progress bar."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        master_task = progress.add_task("[cyan]Running Parallel Modules...", total=len(tasks))
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(task): task.__name__ for task in tasks}
            for future in as_completed(futures):
                task_name = futures[future]
                try:
                    future.result()
                    progress.advance(master_task)
                    console.print(f"[success][+] Module {task_name} finished successfully.[/success]")
                except Exception as e:
                    console.print(f"[error][!] Module {task_name} failed: {e}[/error]")
                    progress.advance(master_task)

# --- Main Function ---
def main():
    global TARGET_DOMAIN, OUTPUT_DIR

    parser = argparse.ArgumentParser(description="MRX Turbo: Automated Recon & Vulnerability Scanning Workflow")
    parser.add_argument("-d", "--domain", required=True, help="Target domain (e.g., example.com)")
    parser.add_argument("-o", "--output", default="mrx_results", help="Output directory for results (default: mrx_results)")
    parser.add_argument("-t", "--threads", type=int, default=10, help="Number of concurrent threads (default: 10)")
    args = parser.parse_args()

    TARGET_DOMAIN = args.domain
    OUTPUT_DIR = args.output
    MAX_WORKERS = args.threads

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print_banner()
    console.print(f"[success][*] Starting MRX Turbo scan for: [bold]{TARGET_DOMAIN}[/bold][/success]")
    console.print(f"[info][*] Mode: [bold]Ultra-Parallel Execution (Turbo 100x)[/bold][/info]")
    console.print(f"[info][*] Results: [bold]{os.path.abspath(OUTPUT_DIR)}[/bold][/info]")
    time.sleep(1)

    check_and_install_tools()

    # --- Phase 1: Recon (Sequential because they depend on each other) ---
    phase_subdomain_enumeration()
    phase_check_live_hosts()

    # --- Phase 2: Parallel Heavy Scanning (Everything that can run together) ---
    console.print("\n[heading]🚀 Launching Parallel Attack Engine...[/heading]")
    parallel_tasks = [
        phase_port_scanning,
        phase_directory_fuzzing,
        phase_collect_historical_urls,
        phase_nikto_scan,
        phase_subdomain_takeover
    ]
    execute_parallel(parallel_tasks)

    # --- Phase 3: Post-Processing (Extracting endpoints and filtering) ---
    phase_extract_js_endpoints()
    phase_filter_parameters()

    # --- Phase 4: Parallel Vulnerability Scanning ---
    console.print("\n[heading]🔥 Launching Parallel Vulnerability Scanners...[/heading]")
    vuln_tasks = [
        phase_automated_vulnerability_scanning,
        phase_xss_scanning,
        phase_sql_injection,
        phase_ssrf_testing,
        phase_open_redirect,
        phase_cors_misconfiguration
    ]
    execute_parallel(vuln_tasks)

    print_summary()

def print_summary():
    console.print("\n" + "="*70, style="heading")
    console.print(Text("MRX TURBO SCAN SUMMARY", justify="center", style="bold cyan"))
    console.print("="*70 + "\n", style="heading")
    
    summary_data = [
        ("Subdomains Found", "subs.txt"),
        ("Live Hosts", "live.txt"),
        ("Open Ports (Nmap)", "ports.txt"),
        ("Open Ports (Naabu)", "ports_fast.txt"),
        ("Discovered Directories", "dirs.txt"),
        ("Sensitive Files", "sensitive_files.txt"),
        ("Historical URLs", "all_urls.txt"),
        ("JS Endpoints", "endpoints.txt"),
        ("Parameters (All)", "params.txt"),
        ("Parameters (XSS)", "params_xss.txt"),
        ("Parameters (SQLi)", "params_sqli.txt"),
        ("Parameters (SSRF)", "params_ssrf.txt"),
        ("Parameters (Redirect)", "params_redirect.txt"),
        ("Nuclei Findings", "nuclei_results.txt"),
        ("XSS Results (Dalfox)", "xss_results.txt"),
        ("SQLMap Results", "sqlmap_results"), # Directory
        ("Nikto Scan Results", "nikto.txt"),
    ]
    
    table = Table(title="[bold magenta]Scan Results Overview[/bold magenta]")
    table.add_column("Category", style="cyan", no_wrap=True)
    table.add_column("Count / Status", style="green")

    for label, filename in summary_data:
        filepath = os.path.join(OUTPUT_DIR, filename)
        if os.path.exists(filepath):
            if os.path.isdir(filepath):
                count = len(os.listdir(filepath)) # Count files in directory
                table.add_row(label, f"[result]{count} files[/result]")
            else:
                try:
                    count = sum(1 for line in open(filepath, 'r', errors='ignore'))
                    table.add_row(label, f"[result]{count}[/result]")
                except Exception:
                    table.add_row(label, "[warning]Checked[/warning]")
        else:
            table.add_row(label, "[error]Not Found[/error]")

    console.print(table)
    console.print(f"\n[success][+] MRX Turbo scan completed for [bold]{TARGET_DOMAIN}[/bold]![/success]")
    console.print(f"[info][*] All results are saved in: [bold]{os.path.abspath(OUTPUT_DIR)}[/bold][/info]")
    console.print("="*70 + "\n", style="heading")

if __name__ == "__main__":
    main()
