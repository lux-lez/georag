 # Try relative import (works when run as a package: python3 -m georag ... )
try: from .cli import interface

# Fallback to absolute import (works when run as a script: python3 georag ... )
except ImportError: from cli import interface #TODO: not working yet... 

if __name__ == "__main__": interface()


