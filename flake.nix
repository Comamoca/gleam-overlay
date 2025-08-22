{
  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
  };

  outputs =
    { self, nixpkgs }:
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
      devShells = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        {
          default = pkgs.mkShell {
            packages = with pkgs; [
              nil
              python312Packages.python-lsp-server
            ];
            shellHook = '''';
          };
        }
      );

      packages = forAllSystems (system:
        let
          pkgs = import nixpkgs { inherit system; };
          gleamPackage = import ./gleam.nix { inherit pkgs; }; 
          gleam = gleamPackage.bin.latest;
        in
        {
          default = gleam;
          nightly = gleamPackage.bin.nightly;
        }
      );

      overlays = {
        default = self: super: {
          gleam = import ./gleam.nix { pkgs = super; };
        };
      };
    };
}
