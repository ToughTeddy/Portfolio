from pprint import pprint

try:
    from propose_reject import ProposeReject  # your class file
except Exception as e:
    print("ERROR: Could not import ProposeReject from propose_reject.py")
    print("Make sure propose_reject.py is in the same folder and defines class ProposeReject.")
    print("Import error was:", repr(e))
    raise


def print_section(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def show_internals(pr: ProposeReject):
    print_section("Names (group1 / group2)")
    print("group1_names:", pr.group1_names)
    print("group2_names:", pr.group2_names)

    if hasattr(pr, "S1"):
        print("S1:", pr.S1)
    if hasattr(pr, "S2"):
        print("S2:", pr.S2)

    print_section("Tiers (group1_tiers / group2_tiers)")
    pprint(pr.group1_tiers)
    pprint(pr.group2_tiers)

    print_section("Rank maps")
    print("group1_rank_of_group2 (for each g1 member: opponent -> rank)")
    pprint(pr.group1_rank_of_group2)
    print("group2_rank_of_group1 (for each g2 member: opponent -> rank)")
    pprint(pr.group2_rank_of_group1)

    print_section("Free flags (initial)")
    print("free_g1:", pr.free_g1)
    print("free_g2:", pr.free_g2)


def run_case(label: str, group1, group2, *, cap_g2=None):
    print_section(f"Constructing ProposeReject  [label={label}]")
    if cap_g2 is None:
        pr = ProposeReject(group1, group2, label=label, strict=False)
    else:
        pr = ProposeReject(group1, group2, label=label, strict=False, cap_g2=cap_g2)

    print("label:", pr.label)
    show_internals(pr)

    print_section("Attempt matching")
    m1, m2 = pr.match()
    print("group1 -> group2:", m1)
    print("group2 -> group1:", m2)
    print_section("Done with this case")


def main():
    # -------- Base inputs (with ties via equal ranks) --------
    group1 = {
        "john": [(1, "beth"),  (2, "cindy"), (2, "anna")],
        "bill": [(1, "cindy"), (2, "beth"),  (3, "anna")],
        "joe":  [(1, "anna"),  (2, "cindy"), (2, "beth")],
    }
    group2 = {
        "beth":  [(1, "john"), (2, "bill"), (2, "joe")],
        "cindy": [(1, "bill"), (2, "john"), (3, "joe")],
        "anna":  [(1, "joe"),  (2, "john"), (2, "bill")],
    }

    # ---------- Case 1: one_to_one ----------
    print("\nCase 1:")
    run_case("one_one", group1, group2)

    # ---------- Case 2: many_to_one ----------
    # Add extra people to see capacity effects
    group1_many = dict(group1)
    group1_many.update({
        "max": [(1, "beth"), (2, "cindy"), (3, "anna")],
        "sam": [(1, "beth"), (2, "anna"),  (3, "cindy")],
    })
    # Let "beth" accept 2; others 1
    caps = {"beth": 2, "cindy": 1, "anna": 1}

    print("\nCase 2:")
    run_case("many_one", group1_many, group2, cap_g2=caps)


if __name__ == "__main__":
    main()