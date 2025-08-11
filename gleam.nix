{
  pkgs ? import <nixpkgs> { },
}:
let
  hashes = pkgs.lib.importJSON ./gleam_hashes.json;

  mkGleamBinary =
    version: archData:
    pkgs.stdenv.mkDerivation rec {
      pname = "gleam";
      inherit version;

      src = pkgs.fetchurl {
        url = archData.url;
        sha256 = archData.sha256;
      };

      unpackPhase = ''
        tar -xf $src
      '';

      installPhase = ''
        runHook preInstall

        mkdir -p $out/bin
        cp gleam $out/bin/
        chmod +x $out/bin/gleam

        runHook postInstall
      '';

      meta = with pkgs.lib; {
        description = "A friendly language for building type-safe, scalable systems";
        homepage = "https://gleam.run";
        license = licenses.asl20;
        platforms = [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ];
      };
    };

  getCurrentArch =
    if pkgs.stdenv.isDarwin then
      if pkgs.stdenv.isAarch64 then "aarch64-darwin" else "x86_64-darwin"
    else if pkgs.stdenv.isLinux then
      if pkgs.stdenv.isAarch64 then "aarch64-linux" else "x86_64-linux"
    else if pkgs.stdenv.hostPlatform.isWindows then
      if pkgs.stdenv.isAarch64 then "aarch64-windows" else "x86_64-windows"
    else
      throw "Unsupported platform";

  gleamVersions = builtins.mapAttrs (
    version: platforms:
    let
      currentArch = getCurrentArch;
    in
    if builtins.hasAttr currentArch platforms then
      mkGleamBinary version platforms.${currentArch}
    else
      throw "Architecture ${currentArch} not supported for Gleam version ${version}"
  ) (builtins.removeAttrs hashes [ "latest" ]);

in
rec {
  bin = gleamVersions // {
    latest =
      let
        currentArch = getCurrentArch;
        latestPlatforms = hashes.latest or (throw "No latest version found in hashes");
      in
      if builtins.hasAttr currentArch latestPlatforms then
        mkGleamBinary "latest" latestPlatforms.${currentArch}
      else
        throw "Architecture ${currentArch} not supported for latest Gleam version";
  } // gleamVersions;
}
