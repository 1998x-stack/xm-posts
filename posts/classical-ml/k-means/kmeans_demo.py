"""Minimal deterministic 1D Lloyd k-means; no third-party dependencies.
This illustrates coordinate descent, not scikit-learn's empty-cluster policy.
"""

POINTS = (0.0, 2.0, 8.0, 10.0)


def inertia(points, centers, labels):
    return sum((x - centers[j]) ** 2 for x, j in zip(points, labels))


def assign(points, centers):
    # Python min breaks equal-distance ties using the smaller index.
    return tuple(min(range(len(centers)), key=lambda j: (x - centers[j]) ** 2)
                 for x in points)


def update(points, centers, labels):
    new = []
    for j, old in enumerate(centers):
        assigned = [x for x, lab in zip(points, labels) if lab == j]
        # Teaching policy: retain previous center for an empty cluster.
        new.append(sum(assigned) / len(assigned) if assigned else old)
    return tuple(new)


def run(points=POINTS, init=(0.0, 2.0), max_iter=30):
    centers = tuple(init)
    history = []
    for _ in range(max_iter):
        labels = assign(points, centers)
        before = inertia(points, centers, labels)
        next_centers = update(points, centers, labels)
        after = inertia(points, next_centers, labels)
        assert after <= before + 1e-12
        history.append((before, after, labels, next_centers))
        if all(abs(a - b) < 1e-12 for a, b in zip(next_centers, centers)):
            break
        centers = next_centers
    return next_centers, assign(points, next_centers), history


if __name__ == "__main__":
    centers, labels, history = run()
    assert centers == (1.0, 9.0), centers
    assert labels == (0, 0, 1, 1), labels
    assert inertia(POINTS, centers, labels) == 4.0
    print("centers:", centers, "labels:", labels, "inertia:", 4.0)
