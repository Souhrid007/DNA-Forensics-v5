import hashlib


# Common STR loci (just an example subset)
DEFAULT_STR_LOCI = [
    "D3S1358",
    "vWA",
    "FGA",
    "TH01",
    "TPOX",
    "CSF1PO",
    "D5S818",
    "D7S820",
    "D8S1179",
]


def _alleles_from_hash(seed: str, min_allele: int = 8, max_allele: int = 28):
    """
    Internal helper: from a seed string, generate two allele values
    in [min_allele, max_allele].
    """
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    # use first two bytes for two alleles
    a1 = min_allele + (digest[0] % (max_allele - min_allele + 1))
    a2 = min_allele + (digest[1] % (max_allele - min_allele + 1))
    return str(a1), str(a2)


def generate_mock_str_profile(sample):
    """
    Generate a deterministic mock STR profile for a sample.

    This does NOT do real bioinformatics. It creates plausible
    locus -> [allele1, allele2] pairs based on sample_id.
    """
    loci_data = {}

    for locus in DEFAULT_STR_LOCI:
        # unique seed for each locus + sample
        seed = f"{sample.sample_id}-{locus}"
        a1, a2 = _alleles_from_hash(seed)
        loci_data[locus] = [a1, a2]

    profile = {
        "sample_id": sample.sample_id,
        "case_id": sample.case.case_id,
        "loci": loci_data,
    }
    return profile
