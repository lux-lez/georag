 # Try relative import (works when run as a package)
try: from .cli import interface

# Fallback to absolute import (works when run as a script)
except ImportError: from cli import interface

if __name__ == "__main__": interface()


