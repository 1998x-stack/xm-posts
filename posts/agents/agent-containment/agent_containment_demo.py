"""A teaching-only workspace path boundary.

Production isolation also requires OS/kernel controls, race-safe file access,
mount policy, process restrictions, network egress policy, and auditing.
"""
from pathlib import Path


def inside_workspace(workspace, candidate):
    root = Path(workspace).resolve()
    target = Path(candidate).resolve()
    try:
        target.relative_to(root)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    print("Use inside_workspace() before granting a workspace-scoped file action.")
