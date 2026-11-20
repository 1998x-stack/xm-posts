"""A tiny positive RDFS-style closure demo; intentionally not a full OWL reasoner."""
from __future__ import annotations

Triple = tuple[str, str, str]

EXAMPLE_TRIPLES: tuple[Triple, ...] = (
    ("ResearchStudent", "rdfs:subClassOf", "Student"),
    ("Student", "rdfs:subClassOf", "Person"),
    ("enrolledIn", "rdfs:domain", "Student"),
    ("enrolledIn", "rdfs:range", "Course"),
    ("alice", "rdf:type", "ResearchStudent"),
    ("alice", "enrolledIn", "CS101"),
)


def infer(triples: tuple[Triple, ...] | set[Triple]) -> set[Triple]:
    """Apply subclass, domain, and range rules until no new triples appear."""
    facts = set(triples)
    while True:
        additions: set[Triple] = set()
        subclasses = [(s, o) for s, p, o in facts if p == "rdfs:subClassOf"]
        domains = [(s, o) for s, p, o in facts if p == "rdfs:domain"]
        ranges = [(s, o) for s, p, o in facts if p == "rdfs:range"]

        for subject, predicate, obj in facts:
            if predicate == "rdf:type":
                for child, parent in subclasses:
                    if obj == child:
                        additions.add((subject, "rdf:type", parent))
            for property_iri, domain_class in domains:
                if predicate == property_iri:
                    additions.add((subject, "rdf:type", domain_class))
            for property_iri, range_class in ranges:
                if predicate == property_iri:
                    additions.add((obj, "rdf:type", range_class))

        for child, parent in subclasses:
            for middle, ancestor in subclasses:
                if parent == middle:
                    additions.add((child, "rdfs:subClassOf", ancestor))

        new_facts = additions - facts
        if not new_facts:
            return facts
        facts.update(new_facts)


if __name__ == "__main__":
    explicit = set(EXAMPLE_TRIPLES)
    inferred = infer(EXAMPLE_TRIPLES) - explicit
    print("Explicit facts:")
    for triple in sorted(explicit):
        print("  ", " ".join(triple))
    print("\nInferred facts:")
    for triple in sorted(inferred):
        print("  ", " ".join(triple))
