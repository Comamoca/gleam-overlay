{
  description = "An example flake for build latest gleam.";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixpkgs-unstable";
    flake-parts.url = "github:hercules-ci/flake-parts";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    rust-overlay.url = "github:oxalica/rust-overlay";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    git-hooks-nix.url = "github:cachix/git-hooks.nix";
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
        inputs.treefmt-nix.flakeModule
        inputs.git-hooks-nix.flakeModule
        inputs.flake-parts.flakeModules.easyOverlay
      ];
      systems = import inputs.systems;

      perSystem =
        {
          config,
          pkgs,
          system,
          ...
        }:
        let
          gleamPackage = import ./gleam.nix { inherit pkgs; };
          gleam = gleamPackage.bin.latest;
        in
        {
          overlayAttrs = {
            inherit (config.packages) gleamPackage;
          };

          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              nixfmt.enable = true;
            };

            settings.formatter = { };
          };

          pre-commit = {
            check.enable = true;
            settings = {
              hooks = {
                treefmt.enable = true;
                ripsecrets.enable = true;
              };
            };
          };

          devenv.shells.default = {
            packages = with pkgs; [
              nil
              python312Packages.python-lsp-server
            ];

            languages = {
              gleam = {
                enable = true;
                package = gleam;
              };
              python = {
                enable = true;
                uv = {
                  enable = true;
                  sync.enable = true;
                };
              };
            };

            enterShell = '''';
          };

          packages.default = gleam;
        };
    };
}
