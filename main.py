from calorimetry_tools import *


def convert_from_impc_to_tse_file(gene_symbol):
    """Wrapper to convert from IMPC dataset to a TSE file"""
    # saves multiply files with the IMPC Solr API
    get_measurements_for_gene_symbol(gene_symbol)

    # combine these files and store as data frame
    df = combine_measurements_for_gene_symbol(
        gene_symbol, base_folder="results/"
    )

    # convert df to TSE
    write_tse(df, gene_symbol, f"results/TSE_file_for_{gene_symbol}.csv")


if __name__ == "__main__":
    gene_symbols = ["Ucp1", "Adipoq"]

    for gene_symbol in gene_symbols:
        convert_from_impc_to_tse_file(gene_symbol)
