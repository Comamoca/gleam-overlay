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

The following is an example of gleam-overlay when using [flake-parts](https://flake.parts).

```nix
{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    gleam-overlay.url = "github:Comamoca/gleam-overlay";
  };

  outputs =
    inputs@{
      self,
      systems,
      nixpkgs,
      flake-parts,
      ...
    }:
    flake-parts.lib.mkFlake { inherit inputs; } {
      imports = [
        inputs.devenv.flakeModule
      ];
      systems = import inputs.systems;

      perSystem =
        {
          config,
          pkgs,
          system,
          ...
        }:
        {
           _module.args.pkgs = import inputs.nixpkgs {
             inherit system;
             overlays = [
               inputs.gleam-overlay.overlays.default
             ];
             config = { };
           };

          devenv.shells.default = {
            packages = [ pkgs.nil ];

            languages = {
              gleam = {
                enable = true;
                package = pkgs.gleam.bin."1.10.0";
              };
            };

            enterShell = '''';
          };
        };
    };
}
```

### Direct Usage

```sh
# Run the latest version
nix run github:Comamoca/gleam-overlay

# Use in a shell
nix shell github:Comamoca/gleam-overlay
```

## 🏗️ Supported Platforms

- `aarch64-darwin`
- `aarch64-linux`
- `x86_64-darwin`
- `x86_64-linux`

## 📋 Version & Platform Compatibility

| Version | aarch64-darwin | aarch64-linux | x86_64-darwin | x86_64-linux |
|---------|---------|---------|---------|---------|
| `1.12.0` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc3` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.12.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.11.1` | ✅ | ✅ | ✅ | ✅ |
| `1.11.0` | ✅ | ✅ | ✅ | ✅ |
| `1.11.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.11.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.10.0` | ✅ | ✅ | ✅ | ✅ |
| `1.10.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.9.1` | ✅ | ✅ | ✅ | ✅ |
| `1.9.0` | ✅ | ✅ | ✅ | ✅ |
| `1.9.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.9.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.8.1` | ✅ | ✅ | ✅ | ✅ |
| `1.8.0` | ✅ | ✅ | ✅ | ✅ |
| `1.8.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.7.0` | ✅ | ✅ | ✅ | ✅ |
| `1.7.0-rc3` | ✅ | ✅ | ✅ | ✅ |
| `1.7.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.7.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.6.3` | ✅ | ✅ | ✅ | ✅ |
| `1.6.2` | ✅ | ✅ | ✅ | ✅ |
| `1.6.1` | ✅ | ✅ | ✅ | ✅ |
| `1.6.0` | ✅ | ✅ | ✅ | ✅ |
| `1.6.0-rc2` | ✅ | ✅ | ✅ | ✅ |
| `1.6.0-rc1` | ✅ | ✅ | ✅ | ✅ |
| `1.5.1` | ✅ | ✅ | ✅ | ✅ |
| `1.5.0` | ✅ | ✅ | ✅ | ✅ |
| `1.5.0-rc2` | ✅ | ✅ | ✅ | ✅ |


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
- [deno-overlay](https://github.com/haruki7049/deno-overlay) - I used it as a reference for approaches such as obtaining hashes.
