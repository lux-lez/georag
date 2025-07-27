import os

# Load API key
def get_api_key(filename : str) -> str:
    ext = os.path.splitext(filename)[-1]
    if ext not in [".txt"]: 
        print("Warning! Exptected API key file to be text file.")
    proj_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    apikey_path = os.path.join(proj_dir, ".api_keys", filename)
    try:
        with open(apikey_path, "r") as f:
            token = f.read()
        if "\n" in token:
            print("Warning! Expected API key to only contain single line")
            token = token.split("\n")[0]
        token = token.strip()
    except Exception as e:
        print("API key file ", apikey_path, " not found or corrupt."); return ""   
    return token

def get_token(path:str=""):
    if path == "":
        print("Please enter API key.")
        api_key = input("API Key")
    else:
        try: 
            api_key = get_api_key(path)
        except Exception as e:
            print("No API key found. Please enter API key.")
            api_key = input("API Key")
