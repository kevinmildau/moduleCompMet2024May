# Practical Materials

This repository contains two tutorials on mass spectral networking using GNPS and related tools. This practical is in active development and may be subject to changes.

# Use in google colab
To use the modules in google colab, they should be downloaded from GitHub: the module on experimental data from [*github*](https://github.com/vdhooftcompmet/CompMet_Tutorials/blob/main/practical_may2024.ipynb), and the module using natural products standars from [*github*](https://github.com/vdhooftcompmet/CompMet_Tutorials/blob/main/practical_appendix_natural_products_library.ipynb), uploaded to your *gdrive*, and opened using *Google Colaboratory*. Run the google colab set-up code cell to install all dependencies (beware of the interactive input!).

# Local Set-up and Use:
Make sure to have conda, and git available on your machine and run the following commands to set-up the course module:

```{bash}
conda create --name compMetEnv python=3.10.8
conda activate compMetEnv
git clone https://github.com/vdhooftcompmet/CompMet_Tutorials.git
cd CompMet_Tutorials
pip install .
jupyter-notebook
```

These commands create 1) a new isolated python environment, 2) activate this environmeent, 3) clone the github repository, 4) move the active directory into the downloaded repository folder using the terminal, 5) install the compMetabolomics course modules, and 6) run a jupyter-notebook from within the conda environment. Set-up may differ when using google-colab or hosted jupyterlab environments. 
