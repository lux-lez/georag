# GeoRAG  


## Installation 

This software was built using Python Here are the installation instructions specific to Your platform.

<b>Linux</b> 

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt 
```

Caveat; If you don't have a GPU that supports CUDA then run 
```bash
pip cache purge
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
```
to clear the CUDA files and reinstall the CPU version of torch. Retry the installation steps from above afterwards.  

## How to use 

Just the short version here. 
[For more information read the official documentation.](./docs/Solution.md).

<b> Linux </b>

```bash
source .venv/bin/activate
python3 georag.py
```

Run tests with `sh run_tests.sh`.

To check the disk usage of the data directory per place run
```bash
du -hd1 data
```


## What still needs to be improved

- TODO: installation, run and test instructions for Windows and macOS 

- Recursive website scraping for better information on website 

- Still slow.

- Redundant files, inefficient memory usage