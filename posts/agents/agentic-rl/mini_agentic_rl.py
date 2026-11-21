"""A deterministic toy environment for teaching Agentic RL trajectories.

This is an environment example, not an RL trainer or benchmark reproduction.
"""
from __future__ import annotations

from typing import Iterable


class DirectoryEnv:
    """A tiny partially observed directory lookup task."""

    def reset(self) -> str:
        self._team: str | None = None
        self._lead: str | None = None
        self._done = False
        self._steps = 0
        return "Goal: find the team and lead for project Orion."

    def step(self, action: str) -> tuple[str, float, bool]:
        if self._done:
            raise RuntimeError("episode already terminated")

        self._steps += 1
        if action == "search_project":
            self._team = "Atlas"
            return "Observation: Orion belongs to the Atlas team.", 0.0, False

        if action == "lookup_lead":
            if self._team is None:
                return "Observation: error; search the project first.", -0.1, False
            self._lead = "Mina"
            return "Observation: the Atlas team lead is Mina.", 0.0, False

        if action.startswith("answer:"):
            answer = action.split(":", 1)[1]
            reward = 1.0 if self._lead is not None and answer == self._lead else 0.0
            self._done = True
            return ("Observation: answer accepted." if reward else
                    "Observation: answer rejected."), reward, True

        return "Observation: unknown tool.", -0.1, False


def discounted_returns(rewards: Iterable[float], gamma: float = 0.99) -> list[float]:
    """Compute reward-to-go for a finite trajectory."""
    if not 0.0 <= gamma <= 1.0:
        raise ValueError("gamma must be in [0, 1]")
    values = list(rewards)
    result = [0.0] * len(values)
    running = 0.0
    for index in range(len(values) - 1, -1, -1):
        running = float(values[index]) + gamma * running
        result[index] = running
    return result


def run_episode(actions: Iterable[str]) -> list[dict[str, object]]:
    """Run a fixed action sequence and return its observed trajectory."""
    env = DirectoryEnv()
    env.reset()
    trajectory: list[dict[str, object]] = []
    for action in actions:
        observation, reward, done = env.step(action)
        trajectory.append({
            "action": action,
            "observation": observation,
            "reward": reward,
            "done": done,
        })
        if done:
            break
    return trajectory


if __name__ == "__main__":
    actions = ["search_project", "lookup_lead", "answer:Mina"]
    trajectory = run_episode(actions)
    rewards = [float(step["reward"]) for step in trajectory]
    for step in trajectory:
        print(step)
    print("discounted returns:", discounted_returns(rewards, gamma=0.9))
