"""Small, dependency-light estimators for discrete information diagnostics.

The historical Arena artifacts contain categorical, auditable features rather
than calibrated probabilities.  This module therefore uses plugin estimates
for conditional mutual information and an MMI-style two-source PID proxy.
These are descriptive estimators; callers should report sample sizes and null
comparisons alongside the returned values.
"""

from collections import Counter, defaultdict
import math
import random
from statistics import median
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


def _freeze(value: Any) -> Any:
    """Make common JSON-like values hashable for categorical counting."""
    if isinstance(value, Mapping):
        return tuple(sorted((key, _freeze(item)) for key, item in value.items()))
    if isinstance(value, (list, tuple, set)):
        return tuple(_freeze(item) for item in value)
    return value


def _conditioning_key(row: Mapping[str, Any], conditioning: Sequence[str]) -> Any:
    values = tuple(_freeze(row.get(column)) for column in conditioning)
    return values[0] if len(values) == 1 else values


def conditional_mutual_information(
    rows: Iterable[Mapping[str, Any]],
    source: str,
    target: str,
    conditioning: Sequence[str] = (),
) -> float:
    """Estimate I(source; target | conditioning) in bits.

    The plugin estimator is intentionally simple and auditable.  It skips rows
    with missing fields and returns zero when no variation is available.
    """
    usable: List[Tuple[Any, Any, Any]] = []
    for row in rows:
        x = _freeze(row.get(source))
        y = _freeze(row.get(target))
        z = _conditioning_key(row, conditioning)
        if x is None or y is None or z is None and conditioning:
            continue
        usable.append((x, y, z))

    if not usable:
        return 0.0

    joint = Counter(usable)
    source_condition = Counter((x, z) for x, _, z in usable)
    target_condition = Counter((y, z) for _, y, z in usable)
    condition = Counter(z for _, _, z in usable)
    total = len(usable)
    value = 0.0
    for (x, y, z), count in joint.items():
        denominator = source_condition[(x, z)] * target_condition[(y, z)]
        if denominator == 0:
            continue
        ratio = (count * condition[z]) / denominator
        value += (count / total) * math.log2(ratio)
    # Tiny negative values can occur from floating-point arithmetic.
    return max(0.0, value)


def joint_source(
    rows: Iterable[Mapping[str, Any]],
    sources: Sequence[str],
    output: str = "__joint_source__",
) -> List[Dict[str, Any]]:
    """Return row copies with a tuple-valued joint source column."""
    result: List[Dict[str, Any]] = []
    for row in rows:
        copied = dict(row)
        copied[output] = tuple(_freeze(row.get(source)) for source in sources)
        result.append(copied)
    return result


def roundwise_rjig(
    rows: Sequence[Mapping[str, Any]],
    group_source: str,
    individual_sources: Sequence[str],
    target: str,
    conditioning: Sequence[str] = (),
) -> Dict[str, Any]:
    """Compute pooled-source CMI, best individual CMI, and their contrast."""
    group_information = conditional_mutual_information(
        rows, group_source, target, conditioning
    )
    individual_information = {
        source: conditional_mutual_information(rows, source, target, conditioning)
        for source in individual_sources
    }
    best_source = None
    best_information = 0.0
    if individual_information:
        best_source, best_information = max(
            individual_information.items(), key=lambda item: item[1]
        )
    return {
        "group_information_bits": group_information,
        "best_individual_information_bits": best_information,
        "best_individual_source": best_source,
        "rjig_bits": group_information - best_information,
        "individual_information_bits": individual_information,
        "rows": len(rows),
    }


def mmi_pid_synergy(
    rows: Sequence[Mapping[str, Any]],
    source_i: str,
    source_j: str,
    target: str,
    conditioning: Sequence[str] = (),
) -> Dict[str, float]:
    """Return an MMI-style conditional two-source PID proxy.

    Redundancy is ``min(I_i, I_j)`` and synergy is the joint information above
    the stronger individual source.  This is deliberately named an MMI proxy,
    not a full Williams-Beer I_min implementation.
    """
    i_i = conditional_mutual_information(rows, source_i, target, conditioning)
    i_j = conditional_mutual_information(rows, source_j, target, conditioning)
    joint_rows = joint_source(rows, (source_i, source_j))
    i_joint = conditional_mutual_information(
        joint_rows, "__joint_source__", target, conditioning
    )
    redundancy = min(i_i, i_j)
    return {
        "unique_i_bits": max(0.0, i_i - redundancy),
        "unique_j_bits": max(0.0, i_j - redundancy),
        "redundancy_bits": redundancy,
        "synergy_bits": max(0.0, i_joint - max(i_i, i_j)),
        "joint_information_bits": i_joint,
        "individual_i_bits": i_i,
        "individual_j_bits": i_j,
    }


def median_pairwise_synergy(
    rows: Sequence[Mapping[str, Any]],
    sources: Sequence[str],
    target: str,
    conditioning: Sequence[str] = (),
) -> Dict[str, Any]:
    """Summarize MMI-proxy synergy across all available source pairs."""
    values: List[float] = []
    pairs: Dict[str, Dict[str, float]] = {}
    for index, source_i in enumerate(sources):
        for source_j in sources[index + 1 :]:
            result = mmi_pid_synergy(
                rows, source_i, source_j, target, conditioning
            )
            key = f"{source_i}|{source_j}"
            pairs[key] = result
            values.append(result["synergy_bits"])
    return {
        "median_synergy_bits": median(values) if values else 0.0,
        "pairs": pairs,
        "pair_count": len(values),
    }


def permutation_null(
    rows: Sequence[Mapping[str, Any]],
    source: str,
    target: str,
    conditioning: Sequence[str] = (),
    permutations: int = 100,
    seed: int = 0,
) -> Dict[str, Any]:
    """Shuffle a source within conditioning strata and recompute CMI."""
    observed = conditional_mutual_information(rows, source, target, conditioning)
    if not rows or permutations <= 0:
        return {
            "observed_bits": observed,
            "null_median_bits": 0.0,
            "null_mean_bits": 0.0,
            "p_value_ge_observed": 1.0,
            "permutations": 0,
        }

    rng = random.Random(seed)
    grouped: Dict[Any, List[int]] = defaultdict(list)
    for index, row in enumerate(rows):
        grouped[_conditioning_key(row, conditioning)].append(index)

    null_values: List[float] = []
    for _ in range(permutations):
        shuffled = [dict(row) for row in rows]
        for indices in grouped.values():
            values = [rows[index].get(source) for index in indices]
            rng.shuffle(values)
            for index, value in zip(indices, values):
                shuffled[index][source] = value
        null_values.append(
            conditional_mutual_information(shuffled, source, target, conditioning)
        )

    exceedances = sum(value >= observed for value in null_values)
    return {
        "observed_bits": observed,
        "null_median_bits": median(null_values),
        "null_mean_bits": sum(null_values) / len(null_values),
        "p_value_ge_observed": (exceedances + 1) / (len(null_values) + 1),
        "permutations": len(null_values),
    }
