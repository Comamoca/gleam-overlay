#!/usr/bin/env python3
import json
from pathlib import Path
from typing import Dict, List
from jinja2 import Template

def load_gleam_hashes() -> Dict:
    """Load gleam_hashes.json file"""
    file_path = Path(__file__).parent.parent / "gleam_hashes.json"
    with open(file_path, 'r') as f:
        return json.load(f)

def extract_versions(gleam_data: Dict) -> List[str]:
    """Extract and sort version list from gleam_hashes.json"""
    versions = []
    
    for version in gleam_data.keys():
        if version == "latest":
            continue
        versions.append(version)
    
    # Sort versions in descending order (newer versions first)
    def version_sort_key(version: str):
        # Handle special versions like 'nightly'
        if version == "nightly":
            return (0, 0, 0, -1, 0)  # Put nightly at the end
        # Handle release candidates and versions with additional suffixes
        if "-rc" in version:
            base_version, rc_part = version.split("-rc", 1)
            rc_num = int(rc_part) if rc_part.isdigit() else 0
            # RC versions should come after the main version but before the next version
            return tuple(map(int, base_version.split("."))) + (0, rc_num)
        else:
            return tuple(map(int, version.split("."))) + (1, 0)  # Regular versions get higher priority
    
    versions.sort(key=version_sort_key, reverse=True)
    return versions

def get_supported_platforms(gleam_data: Dict) -> List[str]:
    """Get list of supported platforms"""
    platforms = set()
    for version_data in gleam_data.values():
        if isinstance(version_data, dict):
            platforms.update(version_data.keys())
    
    return sorted(list(platforms))

def generate_versions_table(versions: List[str]) -> str:
    """Generate markdown table for versions"""
    table = "| Version | Package Name |\n"
    table += "|---------|-------------|\n"
    
    for version in versions:
        package_name = f"gleam-{version.replace('.', '_').replace('-', '_')}"
        table += f"| `{version}` | `{package_name}` |\n"
    
    # Add latest alias
    table += f"| `latest` | `gleam-latest` (alias for `{versions[0]}`) |\n"
    
    return table

def generate_platform_version_matrix(gleam_data: Dict, versions: List[str], platforms: List[str]) -> str:
    """Generate markdown table showing platform support for each version"""
    # Create header
    table = "| Version |"
    for platform in platforms:
        table += f" {platform} |"
    table += "\n"
    
    # Create separator
    table += "|---------|"
    for _ in platforms:
        table += "---------|"
    table += "\n"
    
    # Add rows for each version
    for version in versions:
        table += f"| `{version}` |"
        version_data = gleam_data.get(version, {})
        for platform in platforms:
            if platform in version_data:
                table += " ✅ |"
            else:
                table += " ❌ |"
        table += "\n"
    
    return table

def generate_platforms_list(platforms: List[str]) -> str:
    """Generate markdown list for platforms"""
    platform_list = ""
    for platform in platforms:
        platform_list += f"- `{platform}`\n"
    return platform_list.rstrip()

def generate_readme_content(gleam_data: Dict, versions: List[str], platforms: List[str]) -> str:
    """Generate README.md content using template"""
    # Load template
    template_path = Path(__file__).parent.parent / "doc_templates" / "README.md.j2"
    with open(template_path, 'r') as f:
        template_content = f.read()
    
    template = Template(template_content)
    
    # Generate content components
    versions_table = generate_versions_table(versions)
    platforms_list = generate_platforms_list(platforms)
    platform_version_matrix = generate_platform_version_matrix(gleam_data, versions, platforms)
    
    # Render template
    return template.render(
        versions_table=versions_table,
        platforms_list=platforms_list,
        platform_version_matrix=platform_version_matrix
    )

def main():
    """Main function to generate README.md"""
    try:
        # Load data
        gleam_data = load_gleam_hashes()
        
        # Extract versions and platforms
        versions = extract_versions(gleam_data)
        platforms = get_supported_platforms(gleam_data)
        
        # Generate README content
        readme_content = generate_readme_content(gleam_data, versions, platforms)
        
        # Write README.md
        readme_path = Path(__file__).parent.parent / "README.md"
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"Generated README.md with {len(versions)} versions and {len(platforms)} platforms")
        
    except Exception as e:
        print(f"Error generating README: {e}")
        exit(1)

if __name__ == "__main__":
    main()