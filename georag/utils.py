# All functions with no dependencies, only Python base classes

def alphanumeric(name : str, allow_sep : bool = True) -> str:
    '''
    Alphanumeric representation (ie. a-z or A-Z or 0-9 ) of a string.
    Useful for saving files as alphanumeric strings are guaranteed to be file system compatible across distributions.
    If seperators are allowed this includes "-" (Minus) and "_" (Underscore). 
    This function is useful for generating file names. 
    '''

    name = str(name) 

    # Replace accented and special characters with ASCII equivalents
    replacements = {
        "ä": "a", "Ä": "a", "ã": "a", "å": "a", "á": "a", "à": "a", "â": "a", "æ": "ae",
        "õ": "o", "ö": "o", "ó": "o", "ò": "o", "ô": "o", "ø": "o", "Ô": "I",
        "é": "e", "è": "e", "ê": "e", "ë": "e", "É": "E", "È": "E", "Ê": "E", "Ë": "E",
        "í": "i", "ì": "i", "î": "i", "ï": "i", "Í": "i", "Ì": "I", "Î": "I", "Ï": "I",
        "ñ": "n", "Ñ": "n",
        "ç": "c", "Ç": "c",
        "ß": "ss",
        "ú": "u", "ù": "u", "û": "u", "ü": "u", "Ú": "u", "Ù": "U", "Û": "U", "Ü": "U"
    }
    for orig, repl in replacements.items():
        name = name.replace(orig, repl)

    # Seperators    
    for sep in [" ", ".", ","]:
        name = name.replace(sep, "_")
    for sep in ["−","➖"]:
        name = name.replace(sep, "-")
    while "__" in name:
        name = name.replace("__", "_")

    # Filter alphanumeric digits 
    a_z = "abcdefghijklmnopqrstuvwxyz"
    A_Z = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    dig = "0123456789"
    sep = "_-"          # allow two seperators
    valid_letter = lambda x: x in (a_z + A_Z + dig + sep)
    name  = "".join(filter(valid_letter, list(name)))

    return name


def human_readable_number(num):
    """
    Converts a number to a string with a suffix for thousands (k), millions (M), billions (B), etc.
    Examples:
        10000      -> '10k'
        3324450    -> '3.3M'
        1000000000 -> '1B'
    """
    if num < 1000:
        return str(num)
    elif num < 1_000_000:
        return f"{num/1000:.1f}k".rstrip('0').rstrip('.')
    elif num < 1_000_000_000:
        return f"{num/1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif num < 1_000_000_000_000:
        return f"{num/1_000_000_000:.1f}B".rstrip('0').rstrip('.')
    else:
        return f"{num/1_000_000_000_000:.1f}T".rstrip('0').rstrip('.')
