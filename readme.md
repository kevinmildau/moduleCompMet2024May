# Draft Practical Materials

Clone the repo, and from the command line within the repo clone folder execute the following:

```{bash}
conda create --name moduleCompMet2024May python=3.10
conda activate moduleCompMet2024May
conda install conda-forge::r-base=4.3
pip install .
jupyter-notebook
```

Command explanation:

- set up conda environment with correct python version
- activate the environment
- install r from from conda forge
- install the downloaded moduleCompMet2024May package dependencies and functions for easy access
- open the jupyter-notebook ecosystem in the browser