from typing import List
import pandas as pd
from compMetabolomics.spectrum import Spectrum

def align_with_spectral_feature_id(datadf : pd.DataFrame, spectra: List[Spectrum]):
  """Aligns the datadf dataframe which contains a featur_id column with the ordering of feature_id in a list of spectra."""
  out = pd.DataFrame({'feature_id' : [spec.feature_id for spec in spectra]})
  out = out.merge(datadf, how="inner")
  return out