# From package directory and right environment, install package using: "pip install -e ."   
from setuptools import setup
import os

r_script_sourcepath = os.path.join("msfeast", "runStats.R")

# Read the version string from version.py
version = {}
with open(os.path.join('compMetabolomics', 'version.py')) as fp:
  exec(fp.read(), version)

setup(
  name = 'compMetabolomics',
  version = version["__version__"],
  include_package_data = True, 
  packages = ['compMetabolomics'],
  # scripts = ['someScriptPath.script'],
  python_requires = '>=3.10,<3.11',
  install_requires = [
    'numpy', #'numpy==1.24.4',
    'jupyter', #'jupyter==1.0.0',
    'ipykernel', #"ipykernel==6.28.0",
    'scikit-learn, '#'scikit-learn==1.4.0',
    'scipy', #'scipy==1.10.1',
    'plotly',#'plotly==5.18.0',
    'pandas',#'pandas==2.1.4',
    #'matchms==0.24.1', # required for data pre-processing only
    #"matchmsextras==0.4.0", # required for data pre-processing only
    'kmedoids==0.5.0',
    #'spec2vec==0.8.0',
    #'ms2deepscore==2.0.0', # required for data pre-processing only
    'networkx',
    'dash',
    'dash-cytoscape'
  ],  
  extras_require={
    'dev': ['pytest']
  }
)