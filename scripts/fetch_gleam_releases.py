#!/usr/bin/env python3
import json
import requeste
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
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

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
        print(f"Processing {version}")
        
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
        releases = fetch_gleam_releases()
        assets_data = extract_assets_with_hashes(releases)
        
        output_file = "gleam_hashes.json"
        with open(output_file, "w") as f:
            json.dump(assets_data, f, indent=2)
        
        print(f"Generated {output_file} with {len(assets_data)} entries")
        
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

if __name__ == "__main__":
    main()
