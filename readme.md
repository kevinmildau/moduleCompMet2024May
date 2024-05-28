# Practical Materials

This repository contains a small tutorial on mass spectral networking using GNPS and related tools. This practical is in active development and may be subject to changes.

# Use in google colab
To use the module in google colab, it should be downloaded from [*github*](https://github.com/kevinmildau/moduleCompMet2024May/blob/main/practical_may2024.ipynb), uploaded to your *gdrive*, and opened using *Google Colaboratory*. Run the google colab set-up code cell to install all dependencies (beware of the interactive input!).

# Local Set-up and Use:
Make sure to have conda, and git available on your machine and run the following commands to set-up the course module:

```{bash}
conda create --name moduleCompMet2024May python=3.10.8
conda activate moduleCompMet2024May
git clone https://github.com/kevinmildau/moduleCompMet2024May
cd moduleCompMet2024May
pip install .
jupyter-notebook
```

Command explanation:
- set up conda environment with correct python version
- activate the environment
- install the downloaded moduleCompMet2024May package dependencies and functions for easy access
- open the jupyter-notebook ecosystem in the browser