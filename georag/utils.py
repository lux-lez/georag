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


def strf_big(num):
    """
    String formating for big numbers 
    Converts a number to human readable string with a suffix for thousands (k), millions (M), billions (B), trillions (T)
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

def strf_time(time_ns : float):
    '''
    String formatting for time.
    Converts nanoseconds to a human-readable string with appropriate units:
    - ns (nanoseconds)
    - µs (microseconds)
    - ms (milliseconds)
    - s (seconds)
    - min (minutes)
    - h (hours)
    - d (days)
    - m (months, approx 30.44 days)
    - y (years, approx 365.25 days)

    Examples:
        500         -> '500ns'
        1500        -> '1.5µs'
        2_000_000   -> '2ms'
        65_000_000_000 -> '1.1min'
        3_600_000_000_000 -> '1h'
        31_536_000_000_000_000 -> '1y'
    '''
    units = [
        ('ns', 1),
        ('µs', 1_000),
        ('ms', 1_000_000),
        ('s', 1_000_000_000),
        ('min', 60_000_000_000),
        ('h', 3_600_000_000_000),
        ('d', 86_400_000_000_000),
        ('m', 2_629_746_000_000_000),  # 30.44 days
        ('y', 31_557_600_000_000_000), # 365.25 days
    ]

    for i in range(len(units)-1, -1, -1):
        unit, factor = units[i]
        if time_ns >= factor:
            value = time_ns / factor
            if value < 10:
                value_str = f"{value:.1f}".rstrip('0').rstrip('.')
            else:
                value_str = f"{int(value)}"
            return f"{value_str}{unit}"
    return f"{int(time_ns)}ns"