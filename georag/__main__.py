if __name__ == "__main__": print("Running georag/__main__.py")

 # Try relative import (works when run as a package)
try: from .cli import interface

# Fallback to absolute import (works when run as a script)
except ImportError: from cli import interface

if __name__ == "__main__": interface()

