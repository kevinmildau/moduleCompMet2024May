IN DEVELOPMENT; NOT COMPLETE.

# Practical Materials

This repository contains a small tutorial on mass spectral networking using GNPS and related tools.

# Use in google colab
To use the module in google colab, it should be downloaded from [*github*](), uploaded to you *gdrive*, and opened using *Google Colaboratory*. Run the google colab set-up code cell to install all dependencies.

# Local Set-up and Use:
Clone the repo, and from the command line within the repo clone folder execute the following:

```{bash}
conda create --name moduleCompMet2024May python=3.10.8
conda activate moduleCompMet2024May
pip install .
jupyter-notebook
```

Command explanation:
- set up conda environment with correct python version
- activate the environment
- install the downloaded moduleCompMet2024May package dependencies and functions for easy access
- open the jupyter-notebook ecosystem in the browser


# Useful commands

To remove a folder with content from google colab run: !rm -rf <folder_name>