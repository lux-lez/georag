# GeoRAG  

[Read the official documentation.](./docs/Documentation.md). Here is just the short version:

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

## Usage 


<b> Linux </b>

For the CLI interface run 
```bash
source .venv/bin/activate
python3 georag.py
```

Run an example with `sh run_example.sh`.

Run the tests with `sh run_tests.sh`.

To check the disk usage of the data directory per place run
```bash
du -hd1 data
```



## What still needs to be improved

- Instructions for Windows and macOS: installation, run and test  

- Rather slow, currently hardly any async or parallelization

- Redundancy in file system: currently optimized for rerunning smaller parts of the application, tradeoff is that overall memory is inefficiently used