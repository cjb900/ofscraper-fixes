import requests
from bs4 import BeautifulSoup
import json
import re
import os
import time

# URL of the Bitmovin DRM demo
URL = "https://bitmovin.com/demos/drm"

# Output directory for any downloaded files
OUTPUT_DIR = "drm_files"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Path to ChromeDriver
CHROMEDRIVER_PATH = "C:\\Users\\cjb900\\.cache\\selenium\\chromedriver\\win64\\135.0.7049.95\\chromedriver.exe"

# Log files
NETWORK_LOG = os.path.join(OUTPUT_DIR, "network_requests.txt")
FAIRPLAY_LOG = os.path.join(OUTPUT_DIR, "fairplay_log.txt")

# --- Step 1: Scrape the webpage for links or references to .pem or .bin files ---
def scrape_webpage():
    print("Scraping webpage for references to .pem or .bin files...")
    try:
        response = requests.get(URL, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for links to .pem or .bin files
        for link in soup.find_all("a", href=True):
            href = link["href"]
            if href.endswith(".pem") or href.endswith(".bin"):
                print(f"Found potential file: {href}")
                download_file(href)

        # Look for embedded JavaScript or text references
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string:
                if "private_key.pem" in script.string or "client_id.bin" in script.string:
                    print("Found reference to target files in script content!")
                    print(script.string)
                # Search for FairPlay configuration
                if "fairplay" in script.string.lower():
                    cert_urls = re.findall(r"certificateURL:\s*['\"](https?://[^\s\"']+)['\"]", script.string)
                    la_urls = re.findall(r"LA_URL:\s*['\"](https?://[^\s\"']+)['\"]", script.string)
                    for url in cert_urls + la_urls:
                        print(f"Found FairPlay URL in script: {url}")
                        download_file(url)

    except Exception as e:
        print(f"Error scraping webpage: {e}")

# --- Step 2: Download a file if found ---
def download_file(url, filename=None):
    # Skip placeholder URLs
    if "certificate-url-provided-by-drmtoday" in url or "license-server-url-provided-by-drmtoday" in url:
        print(f"Skipping placeholder URL: {url}")
        return
    try:
        if not url.startswith("http"):
            url = f"https://bitmovin.com{url}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "").lower()
        # Check for .pem or .bin content
        if "pem" in content_type or "bin" in content_type or url.endswith((".pem", ".bin")):
            filename = filename or url.split("/")[-1]
        else:
            filename = filename or "downloaded_file"
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)
        print(f"Downloaded: {filepath}")
        # Log FairPlay-related download
        with open(FAIRPLAY_LOG, "a", encoding="utf-8") as f:
            f.write(f"Downloaded: {url} -> {filepath}\n")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        with open(FAIRPLAY_LOG, "a", encoding="utf-8") as f:
            f.write(f"Error downloading {url}: {e}\n")

# --- Step 3: Parse HLS manifest for FairPlay license URLs ---
def parse_hls_manifest(url):
    print(f"Parsing HLS manifest: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        manifest = response.text
        # Look for #EXT-X-SESSION-KEY or #EXT-X-KEY with FairPlay
        key_lines = re.findall(r'#EXT-X-(SESSION-KEY|KEY):METHOD=([^,]+),URI="([^"]+)"', manifest)
        for key_type, method, uri in key_lines:
            if "SAMPLE-AES" in method:  # FairPlay uses SAMPLE-AES
                print(f"Found FairPlay key URI: {uri}")
                download_file(uri, filename="fairplay_license_response")
                with open(FAIRPLAY_LOG, "a", encoding="utf-8") as f:
                    f.write(f"Found FairPlay key URI: {uri}\n")
    except Exception as e:
        print(f"Error parsing HLS manifest {url}: {e}")
        with open(FAIRPLAY_LOG, "a", encoding="utf-8") as f:
            f.write(f"Error parsing HLS manifest {url}: {e}\n")

# --- Step 4: Capture network requests using Selenium Wire ---
# Note: This implementation uses Selenium Wire in place of native Selenium CDP listeners.
try:
    from seleniumwire import webdriver  # Using Selenium Wire for capturing HTTP requests
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
except ImportError:
    print("Selenium Wire or Selenium is not installed. Please run 'pip install selenium-wire selenium'.")
    exit(1)

def capture_network_requests():
    print("Capturing network requests with Selenium Wire...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    try:
        service = Service(CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        print(f"Error initializing ChromeDriver: {e}")
        print("Ensure ChromeDriver is installed and the path is correct.")
        return []
    
    driver.get(URL)
    
    # Wait a few seconds to allow network traffic to flow
    time.sleep(5)
    
    network_requests = []
    for request in driver.requests:
        if request.response:
            url = request.url
            network_requests.append(url)
            if ".pem" in url or ".bin" in url:
                print(f"Found network request for: {url}")
                download_file(url)
            elif "fairplay" in url.lower() or "certificate" in url.lower() or "license" in url.lower():
                print(f"Potential FairPlay-related network request: {url}")
                download_file(url, filename="fairplay_certificate_response")
            elif url.endswith(".m3u8"):
                print(f"Found HLS manifest: {url}")
                parse_hls_manifest(url)
    
    with open(NETWORK_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(network_requests))
    print(f"Network requests saved to {NETWORK_LOG}")
    driver.quit()
    return network_requests

# --- Step 5: Analyze demo source code for DRM configuration ---
def analyze_demo_source():
    print("Analyzing demo source code...")
    # Example configuration from Bitmovin documentation
    demo_config = """
    var config = {
        key: '<YOUR PLAYER KEY>',
        cast: { enable: true }
    };
    var source = {
        dash: 'https://cdn.bitmovin.com/content/assets/art-of-motion_drm/mpds/11331.mpd',
        hls: 'https://cdn.bitmovin.com/content/assets/art-of-motion_drm/m3u8s/11331.m3u8',
        smooth: 'https://test.playready.microsoft.com/smoothstreaming/SSWSS720H264/SuperSpeedway_720.ism/manifest',
        drm: {
            widevine: { LA_URL: 'https://cwip-shaka-proxy.appspot.com/no_auth' },
            playready: { LA_URL: 'https://test.playready.microsoft.com/service/rightsmanager.asmx?PlayRight=1&ContentKey=EAtsIJQPd5pFiRUrV9Layw==' },
            fairplay: {
                LA_URL: 'https://license-server-url-provided-by-drmtoday',
                certificateURL: 'https://certificate-url-provided-by-drmtoday'
            }
        }
    };
    """
    if "private_key.pem" in demo_config or "client_id.bin" in demo_config:
        print("Found direct reference to target files in demo config!")
    elif "certificateURL" in demo_config:
        print("Found FairPlay certificate URL in demo config!")
        # Attempt to extract and download certificate
        cert_url = re.search(r"certificateURL:\s*'([^']+)'", demo_config)
        if cert_url:
            download_file(cert_url.group(1), filename="fairplay_certificate_config")

# --- Main Execution ---
if __name__ == "__main__":
    print("Starting analysis of Bitmovin DRM demo...")
    scrape_webpage()
    capture_network_requests()
    analyze_demo_source()
    print("Analysis complete. Check the 'drm_files' directory for any downloaded files and 'fairplay_log.txt' for details.")
