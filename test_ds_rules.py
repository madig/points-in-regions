from __future__ import annotations

from typing import Mapping, Union, List, Dict

from test_points_in_regions import Range

# A region selection is either a range or a single value, as a Designspace v5
# axis-subset element only allows a single discrete value or a range for a
# variable-font element.
RegionSelection = Mapping[str, Union[Range, float]]

# A conditionset is a set of named ranges.
ConditionSet = Mapping[str, Range]

# A rule is a list of conditionsets where any has to be relevant for the whole rule to be relevant.
Rule = List[ConditionSet]
Rules = Dict[str, Rule]


def subset_rules(rules: Rules, region_selection: RegionSelection) -> Rules:
    # What rules to keep:
    #  - Keep the rule if any conditionset is relevant.
    #  - A conditionset is relevant if all conditions are relevant or it is empty.
    #  - A condition is relevant if
    #    - axis is point (C-AP),
    #       - and point in condition's range (C-AP-in)
    #       - else (C-AP-out) whole conditionset can be discarded (condition false => conditionset false)
    #    - axis is range (C-AR),
    #       - (C-AR-all) and axis range fully contained in condition range: we can scrap the condition because it's always true
    #       - (C-AR-inter) and intersection(axis range, condition range) not empty: keep the condition with the smaller range (= intersection)
    #       - (C-AR-none) else, whole conditionset can be discarded

    new_rules: Rules = {}
    for rule_name, rule in rules.items():
        new_rule: Rule = []
        for conditionset in rule:
            new_conditionset: ConditionSet = {}
            discard_conditionset = False
            for selection_name, selection_value in region_selection.items():
                # TODO: Ensure that all(key in conditionset for key in region_selection.keys())?
                if selection_name not in conditionset:
                    # raise Exception("Selection has different axes than the rules")
                    continue
                if isinstance(selection_value, (float, int)):  # is point
                    # Case C-AP-in
                    if selection_value in conditionset[selection_name]:
                        # new_conditionset[selection_name] = conditionset[selection_name]
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AP-out
                    else:
                        discard_conditionset = True
                else:  # is range
                    # Case C-AR-all
                    if selection_value in conditionset[selection_name]:
                        pass  # always matches, conditionset can stay empty for this one.
                    # Case C-AR-inter
                    elif (
                        intersection := conditionset[selection_name].intersection(
                            selection_value
                        )
                    ) is not None:
                        new_conditionset[selection_name] = intersection
                    # Case C-AR-none
                    else:
                        discard_conditionset = True
            if not discard_conditionset:
                new_rule.append(new_conditionset)
        if new_rule:
            new_rules[rule_name] = new_rule

    return new_rules


def test_aktiv_rules_subsets() -> None:
    import math

    # All rules
    entire_region: RegionSelection = {
        "Weight": Range(-math.inf, math.inf),
        "Width": Range(-math.inf, math.inf),
        "Italic": Range(-math.inf, math.inf),
    }
    all_rules: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                "Italic": Range(0.1, 1),
            }
        ],
        "BRACKET.601.900": [
            {
                "Weight": Range(601, 900),
                "Width": Range(75, 97.5),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, entire_region) == all_rules

    # All Weight, all Width, Upright only:
    wght_wdth: RegionSelection = {
        "Weight": Range(-math.inf, math.inf),
        "Width": Range(-math.inf, math.inf),
        "Italic": 0,
    }
    rules_wght_wdth: Rules = {
        "BRACKET.601.900": [
            {
                "Weight": Range(601, 900),
                "Width": Range(75, 97.5),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, wght_wdth) == rules_wght_wdth

    # All Weight, normal Width only, Italic only:
    wght: RegionSelection = {
        "Weight": Range(-math.inf, math.inf),
        "Width": 100,
        "Italic": 1,
    }
    rules_wght: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ]
    }
    assert subset_rules(all_rules, wght) == rules_wght

    # All Weight, all Width, Italic only:
    italic_wghtwdth: RegionSelection = {
        "Weight": Range(-math.inf, math.inf),
        "Width": Range(-math.inf, math.inf),
        "Italic": 1,
    }
    rules_italic_wghtwdth: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
        "BRACKET.601.900": [
            {
                "Weight": Range(601, 900),
                "Width": Range(75, 97.5),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, italic_wghtwdth) == rules_italic_wghtwdth

    # All Weight, normal Width only, Italic only:
    italic_wght: RegionSelection = {
        "Weight": Range(-math.inf, math.inf),
        "Width": 100,
        "Italic": 1,
    }
    rules_italic_wght: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, italic_wght) == rules_italic_wght

    # Weight from Bold to Black, Width condensed, Italic 1:
    region1: RegionSelection = {
        "Weight": Range(700, 900),
        "Width": 75,
        "Italic": 1,
    }
    region1_rules: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
        "BRACKET.601.900": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, region1) == region1_rules

    # Wght from Bold to Black, All width, Italic 1:
    region2: RegionSelection = {
        "Weight": Range(700, 900),
        "Width": Range(-math.inf, math.inf),
        "Italic": 1,
    }
    region2_rules: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
        "BRACKET.601.900": [
            {
                # "Weight": Range(-math.inf, math.inf),
                "Width": Range(75, 97.5),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, region2) == region2_rules

    # All Weight, Width from Normal to Extended, Italic 1:
    region3: RegionSelection = {
        "Weight": Range(700, 900),
        "Width": Range(100, 125),
        "Italic": 1,
    }
    region3_rules: Rules = {
        "BRACKET.CYR": [
            {
                # "Weight": Range(-math.inf, math.inf),
                # "Width": Range(-math.inf, math.inf),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, region3) == region3_rules

    # Bold Weight, Width from 0 to 90, Italic 0:
    region4: RegionSelection = {
        "Weight": 700,
        "Width": Range(0, 90),
        "Italic": 0,
    }
    region4_rules: Rules = {
        "BRACKET.601.900": [
            {
                # "Weight": Range(-math.inf, math.inf),
                "Width": Range(75, 90),
                # "Italic": Range(-math.inf, math.inf),
            }
        ],
    }
    assert subset_rules(all_rules, region4) == region4_rules
