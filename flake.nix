{
  description = "A sample Flake for Home Assistant with Python 3.12 & uv";
  
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  
  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python312;
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python
            pkgs.uv
            pkgs.poetry
            python.pkgs.python-lsp-server
            python.pkgs.pytest
          ];
          
          shellHook = ''
            # Set up Poetry environment
            poetry config virtualenvs.in-project true --quiet
            poetry install
            
            # Suppress environment variable output from direnv
            export DIRENV_LOG_FORMAT=""
          '';
        };
      });
}