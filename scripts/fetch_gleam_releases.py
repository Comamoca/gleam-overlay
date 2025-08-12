#!/usr/bin/env python3
import json
import requests
import subprocess
from typing import Dict, List

def get_sha256_hash(url: str) -> str:
    """Calculate SHA256 hash using nix store prefetch-file"""
    
    # Get hash from nix store prefetch-file with --json option
    result = subprocess.run(["nix", "store", "prefetch-file", "--json", "--hash-type", "sha256", url], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"Failed to fetch {url}: {result.stderr}")
    
    # Parse JSON output to extract hash
    try:
        output_data = json.loads(result.stdout.strip())
        return output_data["hash"]
    except (json.JSONDecodeError, KeyError) as e:
        raise Exception(f"Could not parse JSON output: {e}")

def fetch_gleam_releases() -> List[Dict]:
    """Fetch Gleam releases from GitHub API"""
    url = "https://api.github.com/repos/gleam-lang/gleam/releases"
    headers = {'User-Agent': 'gleam-overlay-fetch-script/1.0'}
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    releases = response.json()
    return releases

def fetch_nightly_assets() -> Dict[str, Dict[str, str]]:
    """Fetch nightly assets from GitHub nightly release"""
    nightly_assets = {}
    
    # Nightly build URLs from the actual nightly release
    nightly_urls = {
        "aarch64-darwin": "https://github.com/gleam-lang/gleam/releases/download/nightly/gleam-nightly-aarch64-apple-darwin.tar.gz",
        "aarch64-linux": "https://github.com/gleam-lang/gleam/releases/download/nightly/gleam-nightly-aarch64-unknown-linux-musl.tar.gz", 
        "x86_64-darwin": "https://github.com/gleam-lang/gleam/releases/download/nightly/gleam-nightly-x86_64-apple-darwin.tar.gz",
        "x86_64-linux": "https://github.com/gleam-lang/gleam/releases/download/nightly/gleam-nightly-x86_64-unknown-linux-musl.tar.gz"
    }
    
    headers = {'User-Agent': 'gleam-overlay-fetch-script/1.0'}
    
    for arch, url in nightly_urls.items():
        try:
            # Check if URL exists with HEAD request (follow redirects)
            response = requests.head(url, headers=headers, allow_redirects=True)
            if response.status_code == 200:
                sha256_hash = get_sha256_hash(url)
                nightly_assets[arch] = {
                    "url": url,
                    "sha256": sha256_hash
                }

            else:
                print(f"Nightly asset not available for {arch} (HTTP {response.status_code})")
        except Exception as e:
            print(f"Failed to get nightly hash for {arch}: {e}")
    
    return nightly_assets

def parse_architecture(filename: str) -> str:
    """Parse architecture from filename"""
    arch_mapping = {
        "aarch64-apple-darwin": "aarch64-darwin",
        "aarch64-unknown-linux-musl": "aarch64-linux",
        "x86_64-apple-darwin": "x86_64-darwin",
        "x86_64-unknown-linux-musl": "x86_64-linux",
    }
    
    for key, value in arch_mapping.items():
        if key in filename:
            return value
    
    return "unknown"

def extract_assets_with_hashes(releases: List[Dict]) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Extract asset URLs and calculate their SHA256 hashes, grouped by version"""
    assets_data = {}
    
    for release in releases:
        version = release["tag_name"].lstrip("v")
        version_assets = {}
        
        for asset in release.get("assets", []):
            asset_url = asset["browser_download_url"]
            asset_name = asset["name"]
            
            # Only process binary archives (tar.gz and zip files, not .sha256 or other files)
            if not (asset_name.endswith(".tar.gz") or asset_name.endswith(".zip")) or "sbom" in asset_name:
                continue
                
            arch = parse_architecture(asset_name)
            if arch == "unknown":
                continue
            
            try:
                sha256_hash = get_sha256_hash(asset_url)
                version_assets[arch] = {
                    "url": asset_url,
                    "sha256": sha256_hash
                }
            except Exception as e:
                print(f"Failed to get hash for {asset_name}: {e}")
        
        if version_assets:
            assets_data[version] = version_assets
    
    return assets_data

def main():
    try:
        # Fetch regular releases
        releases = fetch_gleam_releases()
        assets_data = extract_assets_with_hashes(releases)
        
        # Add latest version as alias for the newest release
        if releases and len(assets_data) > 0:
            # Find the latest version (first release in the list from GitHub API)
            latest_version = releases[0]["tag_name"].lstrip("v")
            if latest_version in assets_data:
                assets_data["latest"] = assets_data[latest_version]
        # Try to fetch nightly assets
        try:
            nightly_assets = fetch_nightly_assets()
            if nightly_assets:
                assets_data["nightly"] = nightly_assets
        except Exception as e:
            print(f"Warning: Failed to process nightly builds: {e}")
            print("Continuing with regular releases only...")
        output_file = "gleam_hashes.json"
        with open(output_file, "w") as f:
            json.dump(assets_data, f, indent=2)

        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
