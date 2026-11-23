"""A tiny sparse-object selector for explaining on-demand checkouts.

This is not Scion code: it omits tree traversal, auth, caching, concurrency,
protocol negotiation, and changeset persistence.
"""
def sparse_object_set(objects, requested_paths):
    selected = set()
    for wanted in requested_paths:
        wanted = wanted.rstrip("/")
        for path in objects:
            if path == wanted or path.startswith(wanted + "/"):
                selected.add(path)
    return sorted(selected)


if __name__ == "__main__":
    objects = {
        "src/api/routes.py": b"...",
        "src/api/schema.py": b"...",
        "src/core/loop.py": b"...",
        "docs/guide.md": b"...",
    }
    print(sparse_object_set(objects, ["src/api"]))
