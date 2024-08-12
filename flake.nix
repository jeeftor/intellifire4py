{
  description = "A sample Flake for Home Assistant with Python 3.12 & uv";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

outputs = { self, nixpkgs, flake-utils, ... }:
  flake-utils.lib.eachDefaultSystem (system:
    let
      pkgs = import nixpkgs {
        inherit system;
        overlays = [];
      };
      pythonEnv = pkgs.python312.withPackages (ps: with ps; [        
        
        ps.pip # ensure pip exists        
        ps.numpy # Numpy
 
        # Include any additional Python packages here
      ]);
    in
    {
      devShell = pkgs.mkShell {
        buildInputs = [
          pythonEnv
          pkgs.uv
          pkgs.poetry
          pkgs.python3Packages.python-lsp-server # Python LSP
        ];
         shellHook = ''
          # Config Pow4try
          poetry config virtualenvs.in-project true
          # And now
          poetry install
          
          '';
        };      
    });
}


