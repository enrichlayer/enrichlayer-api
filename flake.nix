{
  description = "EnrichLayer Python API development environment";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=master";

    flake-compat.url = "https://flakehub.com/f/edolstra/flake-compat/1";
    flake-utils.url = "https://flakehub.com/f/numtide/flake-utils/0.1";
  };

  outputs = { self, nixpkgs, flake-utils, ... }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        
        # Build proxycurl-py from PyPI
        proxycurl-py = pkgs.python3.pkgs.buildPythonPackage rec {
          pname = "proxycurl-py";
          version = "0.1.0.post2";
          format = "pyproject";
          
          src = pkgs.python3.pkgs.fetchPypi {
            pname = "proxycurl_py";  # Use underscores to match actual filename
            inherit version;
            sha256 = "cd85fa5183f6ed7bc48bbd53ae2d4f3db4dbcc6f6d04e874f6c7035bc8c55ea3";
          };
          
          nativeBuildInputs = with pkgs.python3.pkgs; [
            poetry-core
          ];
          
          propagatedBuildInputs = with pkgs.python3.pkgs; [
            # Core dependencies - none specified in base package
            
            # AsyncIO extra dependencies
            aiohttp
            
            # Gevent extra dependencies  
            gevent
            requests
            
            # Twisted extra dependencies
            twisted
            treq
          ];
          
          # Skip tests for now
          doCheck = false;
          
          # Add missing __init__.py file for main proxycurl module
          postInstall = ''
            # Create main proxycurl __init__.py if it doesn't exist
            if [ ! -f $out/lib/python*/site-packages/proxycurl/__init__.py ]; then
              echo "# Proxycurl Python API" > $out/lib/python*/site-packages/proxycurl/__init__.py
              echo "# Import default asyncio implementation" >> $out/lib/python*/site-packages/proxycurl/__init__.py  
              echo "from .asyncio import Proxycurl" >> $out/lib/python*/site-packages/proxycurl/__init__.py
            fi
          '';
          
          meta = with pkgs.lib; {
            description = "Python wrapper for Proxycurl API";
            homepage = "https://pypi.org/project/proxycurl-py/";
            license = licenses.mit;
          };
        };
        
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          # Core HTTP dependencies
          aiohttp
          requests
          
          # Async frameworks
          gevent
          twisted
          treq
          
          # Testing dependencies
          pytest
          pytest-asyncio
          pytest-mock
          
          # Development tools
          ruff  # Replaces both black (formatting) and flake8 (linting)
          mypy  # Type checking
          
          # Type stubs
          types-requests
          
          # Build tools
          setuptools
          wheel
          build
          pip
          
          # Additional utilities
          pyyaml
          click
          
          # Our custom proxycurl-py package
          proxycurl-py
        ]);
        
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            pythonEnv
            git
          ];
          
          shellHook = ''
            echo "🚀 EnrichLayer development environment loaded!"
            echo "Python version: $(python --version)"
            echo "Available packages:"
            echo "  - aiohttp (async HTTP client)"
            echo "  - gevent (green threads)"
            echo "  - twisted (async framework)"
            echo "  - pytest (testing)"
            echo "  - ruff, mypy (code quality)"
            echo "  - proxycurl-py (built from source)"
            echo ""
            echo "💡 Run tests with: python test_real_proxycurl_compatibility.py"
            echo "💡 Install package in dev mode: pip install -e ."
          '';
        };
        
        # For CI/CD environments
        packages.default = pythonEnv;
      });
}
