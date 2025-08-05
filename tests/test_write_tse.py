""" Calorimetry tool tests """
from calorimetry_tools import *


def count_lines(file_path):
    """Count lines of file"""
    with open("file_path", "r") as f:
        return sum(1 for _ in f)


def test_write_tse():
    """Wrapper to convert from IMPC dataset to a TSE file"""
    # gene_symbol
    gene_symbol = "Ucp1"

    # saves multiply files with the IMPC Solr API
    get_measurements_for_gene_symbol(gene_symbol)

    # combine these files and store as data frame
    df = combine_measurements_for_gene_symbol(
        gene_symbol, base_folder="results/"
    )

    # convert df to TSE
    write_tse(df, gene_symbol, f"results/TSE_file_for_{gene_symbol}.csv")

    # check lines
    assert count_lines("results/TSE_file_for_{gene_symbol}.csv") == 2386
