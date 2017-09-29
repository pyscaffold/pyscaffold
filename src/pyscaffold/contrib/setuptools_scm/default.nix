{pkgs ? import <nixpkgs> {}}:
with pkgs.pythonPackages;
buildPythonPackage {
  name = "setuptools_scm";
  src = ./.;
  version = "git";
  buildInputs = [
    setuptools
    pip
    pytest
    pkgs.git
    pkgs.mercurial
  ];
}

