{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    poetry2nix = { url = "github:nix-community/poetry2nix"; inputs.nixpkgs.follows = "nixpkgs"; };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = [ "https://devenv.cachix.org" ];
  };

  outputs = { self, nixpkgs, devenv, systems, poetry2nix, ... } @ inputs:
    let
      forEachSystem = nixpkgs.lib.genAttrs (import systems);
    in
    {
      packages = forEachSystem (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          inherit (poetry2nix.lib.mkPoetry2Nix { inherit pkgs; }) mkPoetryApplication;
        in
        {
          # devenv-up = self.devShells.${system}.default.config.procfileScript;

          # make default poetry application
          default = mkPoetryApplication {
            projectDir = ./.;
          };
        });


      devShells = forEachSystem
        (system:
          let
            pkgs = nixpkgs.legacyPackages.${system};
          in
          {

            default = devenv.lib.mkShell {
              inherit inputs pkgs;
              modules = [
                {
                  # https://devenv.sh/reference/options/
                  packages = [ ];

                  languages.python.enable = true;
                  languages.python.poetry.enable = true;
                  languages.python.poetry.activate.enable = true;
                  languages.python.poetry.install.enable = true;

                  # enterShell = ''
                  #   hello
                  # '';

                  # processes.run.exec = "hello";
                }
              ];
            };
          });
    };
}
