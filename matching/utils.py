def compare_loci(loci_a: dict, loci_b: dict):
    """
    Compare two loci dicts: {locus: [a1, a2]}.

    Returns:
        total_score (float): 0.0 to 1.0
        locus_results (list): list of dicts with locus-level info
    """
    locus_results = []
    total = 0.0
    max_total = 0.0

    # union of loci in both
    all_loci = sorted(set(loci_a.keys()) | set(loci_b.keys()))

    for locus in all_loci:
        alleles_a = loci_a.get(locus)
        alleles_b = loci_b.get(locus)

        # Default
        locus_score = 0.0
        match_type = "NO_DATA"

        if alleles_a and alleles_b:
            set_a = set(alleles_a)
            set_b = set(alleles_b)
            intersection = set_a & set_b

            if len(intersection) == 2:
                # perfect match (both alleles match)
                locus_score = 1.0
                match_type = "FULL"
            elif len(intersection) == 1:
                # one allele matches
                locus_score = 0.5
                match_type = "PARTIAL"
            else:
                locus_score = 0.0
                match_type = "NONE"

            max_total += 1.0  # each locus contributes max 1

        elif alleles_a or alleles_b:
            # one side missing
            locus_score = 0.0
            match_type = "MISSING_ONE"
            max_total += 1.0
        else:
            # both missing -> doesn't count
            match_type = "MISSING_BOTH"

        total += locus_score

        locus_results.append({
            "locus": locus,
            "alleles_a": alleles_a,
            "alleles_b": alleles_b,
            "score": locus_score,
            "match_type": match_type,
        })

    overall_score = (total / max_total) if max_total > 0 else 0.0
    return overall_score, locus_results

from strprofiles.models import STRProfile


def search_matches(query_profile: STRProfile):
    """
    Compare a query STRProfile with all other profiles in the database.

    Returns:
        list of dicts: [
          {
            'profile': STRProfile,
            'score': float,
          },
          ...
        ] sorted by score descending
    """
    results = []
    loci_query = query_profile.loci_json

    # all other profiles
    others = STRProfile.objects.exclude(id=query_profile.id).select_related('sample', 'sample__case')

    for prof in others:
        loci_other = prof.loci_json
        score, _ = compare_loci(loci_query, loci_other)
        results.append({
            "profile": prof,
            "score": score,
        })

    # sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results
