<div align="center">

![Last commit](https://img.shields.io/github/last-commit/Comamoca/gleam-overlay?style=flat-square)
![Repository Stars](https://img.shields.io/github/stars/Comamoca/gleam-overlay?style=flat-square)
![Issues](https://img.shields.io/github/issues/Comamoca/gleam-overlay?style=flat-square)
![Open Issues](https://img.shields.io/github/issues-raw/Comamoca/gleam-overlay?style=flat-square)
![Bug Issues](https://img.shields.io/github/issues/Comamoca/gleam-overlay/bug?style=flat-square)

<img src="https://gleam.run/images/lucy/lucy.svg" alt="gleam logo" height="100">

# gleam-overlay

A Nix overlay providing [Gleam](https://gleam.run/) packages for multiple versions and platforms.

</div>

## ✨ Features

- 🚀 Latest Gleam releases with automatic updates
- 🏗️ Multiple architecture support (x86_64/aarch64 Linux/macOS)
- 📦 Easy integration with Nix flakes and traditional overlays
- 🔄 Binary distributions for faster installation

## 🚀 Usage

### With Nix Flakes

Add this overlay to your flake inputs:

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    gleam-overlay.url = "github:Comamoca/gleam-overlay";
  };

  outputs =
    inputs@{ self, nixpkgs, ... }:
    let
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-darwin"
        "x86_64-linux"
      ];

      forAllSystems =
        f:
        builtins.listToAttrs (
          map (system: {
            name = system;
            value = f system;
          }) systems
        );
    in
    {
      devShells = forAllSystems (
        system:
        let
          pkgs = import nixpkgs {
            inherit system;
            overlays = [
              inputs.gleam-overlay.overlays.default
            ];
          };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              pkgs.gleam.bin.latest # Latest version
            ];
            shellHook = '''';
          };
        }
      );
    };
}
```

### With Traditional Overlays

```nix
let
  gleam-overlay = import (fetchTarball "https://github.com/Comamoca/gleam-overlay/archive/main.tar.gz");
  pkgs = import <nixpkgs> { overlays = [ gleam-overlay ]; };
in
{
  environment.systemPackages = [
    pkgs.gleamPackage.bin.latest
    # pkgs.gleamPackage.bin.nightly
  ];
}
```

### Direct Usage

```sh
# Run the latest version
nix run github:Comamoca/gleam-overlay
nix run github:Comamoca/gleam-overlay#nightly

# Use in a shell
nix shell github:Comamoca/gleam-overlay
```

### Build cache

gleam-overlay provides a [cache](https://app.cachix.org/cache/gleam-overlay#pull) via cachix.
In environments with cachix cli, you can use the cache during builds with the following command:

```sh
cachix use gleam-overlay
```

## 🏗️ Supported Platforms

- `aarch64-darwin`
- `aarch64-linux`
- `x86_64-darwin`
- `x86_64-linux`

## 📋 Version & Platform Compatibility

| Version | aarch64-darwin | aarch64-linux | x86_64-darwin | x86_64-linux |
|---------|---------|---------|---------|---------|
| `1.18.1` | ✅ | ✅ | ✅ | ✅ |
| `1.18.0` | ✅ | ✅ | ✅ | ✅ |
| `1.18.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.18.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.17.0` | ✅ | ✅ | ✅ | ✅ |
| `1.17.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.17.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.16.0` | ✅ | ✅ | ✅ | ✅ |
| `1.16.0-rc4` | ✅ | ✅ | ✅ | ✅ |
| `1.16.0-rc3` | ✅ | ✅ | ✅ | ✅ |
| `1.16.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.16.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.15.4` | ✅ | ✅ | ✅ | ✅ |
| `1.15.3` | ✅ | ✅ | ✅ | ✅ |
| `1.15.2` | ✅ | ✅ | ✅ | ✅ |
| `1.15.1` | ✅ | ✅ | ✅ | ✅ |
| `1.15.0` | ✅ | ✅ | ✅ | ✅ |
| `1.15.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.15.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.14.0` | ✅ | ✅ | ✅ | ✅ |
| `1.14.0-rc3` | ✅ | ✅ | ✅ | ✅ |
| `1.14.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.14.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.13.0` | ✅ | ✅ | ✅ | ✅ |
| `1.13.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.13.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc3` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `nightly` | ✅ | ✅ | ✅ | ✅ |


## ⛏️ Development

### Prerequisites

```sh
nix develop
# or
direnv allow
```

### Updating Releases

```sh
cd scripts
python fetch_gleam_releases.py
```

This will update `gleam_hashes.json` with the latest Gleam releases and their checksums.

### Building Manually

```sh
# Build the latest version
nix build

# Build and test
nix flake check
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Gleam](https://gleam.run/) - A friendly language for building type-safe, scalable systems
- The Nix community for excellent tooling and patterns