import os
import pandas as pd

def all_api_keys() -> pd.DataFrame:
    ''' Data frame with all API keys
    Caveat careful when you use this about data safety.
    Returns:
        pd.DataFrame: DataFrame with columns "name" and "password" containing API key
    '''
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = os.path.join(proj_dir, ".api_keys")
    key_files = filter(lambda f: f.endswith(".txt"), os.listdir(key_path))
    key_names = [ f.split(".txt")[0] for f in key_files ]
    key_secrets = [ get_api_key(k) for k in key_names ]
    df = pd.DataFrame({ "name" : key_names, "password" : key_secrets })
    return df

# Load API key from file or enter it manually
def get_api_key(key_name : str) -> str:
    ''' Get API key from file or prompt user to enter it.
    If the key file does not exist, it will be prompted to enter the key
    and saved to a file for future use.
    Args:
        key_name (str): Name of the API key file (without .txt extension).
    Returns:
        str: The API key.
    '''
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    key_path = os.path.join(proj_dir, ".api_keys", key_name + ".txt")
    if os.path.isfile(key_path):
        with open(key_path, "r") as f:
            api_key = f.read()
        api_key = api_key.replace("\n","").strip()
        return api_key
    
    print(key_path, " could not be found")
    api_key = input("Enter API key '" + key_name + "' : ")
    with open(key_path, "w") as f:
        f.write(api_key)
    return api_key
