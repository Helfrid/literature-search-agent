__version__ = "0.1.0"

from .config import set_env_vars

# Initialize environment variables
set_env_vars()


PUBMED_QUERY = """
(
  "Nat Cell Biol"[ta] OR
  "Nature"[ta] OR
  "Nat Struct Mol Biol"[ta] OR
  "Nat Cancer"[ta] OR
  "Nat Rev Mol Cell Biol"[ta] OR
  "Nat Methods"[ta] OR
  "Nat Commun"[ta] OR
  "Cell"[ta] OR
  "Cancer Cell"[ta] OR
  "Mol Cell"[ta] OR
  "Cell Rep"[ta] OR
  "Dev Cell"[ta] OR
  "Cell Stem Cell"[ta] OR
  "Cell Metab"[ta] OR
  "Cell Syst"[ta] OR
  "Trends Cell Biol"[ta] OR
  "Trends Cancer"[ta] OR

  "Science"[ta] OR
  "Sci Transl Med"[ta] OR
  "Sci Adv"[ta] OR
  "Sci Signal"[ta] OR
  "Sci Immunol"[ta] OR

  "EMBO J"[ta] OR
  "EMBO Rep"[ta] OR
  "J Cell Biol"[ta] OR
  "Autophagy"[ta] OR
  "Cell Death Differ"[ta] OR
  "Traffic"[ta] OR
  "J Cell Sci"[ta] OR
  "Cell Mol Life Sci"[ta] OR
  "Cytoskeleton"[ta] OR
  "Mol Biol Cell"[ta] OR
  "BMC Biol"[ta] OR
  "Semin Cell Dev Biol"[ta] OR
  "Curr Opin Cell Biol"[ta] OR
  "Annu Rev Cell Dev Biol"[ta] OR
  "Elife"[ta] OR
  "PLoS Biol"[ta] OR
  "PLoS Genet"[ta] OR

  "Oncogene"[ta] OR
  "Cancer Discov"[ta] OR
  "Clin Cancer Res"[ta] OR
  "Cancer Res"[ta] OR
  "Br J Cancer"[ta] OR
  "Ann Oncol"[ta] OR
  "J Clin Oncol"[ta] OR
  "Lancet Oncol"[ta] OR
  "Cell Death Dis"[ta] OR
  "Carcinogenesis"[ta] OR
  "Neoplasia"[ta] OR
  "Genes Chromosomes Cancer"[ta] OR

  "Nucleic Acids Res"[ta] OR
  "Cell Cycle"[ta] OR
  "Curr Biol"[ta] OR
  "J Biol Chem"[ta] OR
  "J Mol Cell Biol"[ta]
)
"""

PUBMED_QUERY_TEST = """
(
  "Nature"[ta] OR
  "Cell"[ta]
)
"""
