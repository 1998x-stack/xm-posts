from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "posts" / "agents" / "agentic-rl"))

from mini_agentic_rl import DirectoryEnv, discounted_returns, run_episode


def test_successful_three_step_trajectory():
    trajectory = run_episode(["search_project", "lookup_lead", "answer:Mina"])
    assert len(trajectory) == 3
    assert [step["reward"] for step in trajectory] == [0.0, 0.0, 1.0]
    assert trajectory[-1]["done"] is True
    assert "Atlas" in trajectory[0]["observation"]
    assert "Mina" in trajectory[1]["observation"]


def test_environment_feedback_enables_recovery():
    env = DirectoryEnv()
    env.reset()
    observation, reward, done = env.step("lookup_lead")
    assert "search the project first" in observation
    assert reward == -0.1
    assert done is False
    observation, reward, done = env.step("search_project")
    assert "Atlas" in observation
    assert reward == 0.0
    assert done is False


def test_wrong_answer_terminates_without_success_reward():
    env = DirectoryEnv()
    env.reset()
    env.step("search_project")
    env.step("lookup_lead")
    observation, reward, done = env.step("answer:Noah")
    assert "rejected" in observation
    assert reward == 0.0
    assert done is True


def test_discounted_returns_propagate_terminal_reward():
    assert discounted_returns([0.0, 0.0, 1.0], gamma=0.9) == [0.81, 0.9, 1.0]


def test_discounted_returns_empty_and_invalid_gamma():
    assert discounted_returns([]) == []
    try:
        discounted_returns([1.0], gamma=1.1)
    except ValueError as exc:
        assert "gamma" in str(exc)
    else:
        raise AssertionError("invalid gamma should fail")


def test_terminal_environment_rejects_more_actions():
    env = DirectoryEnv()
    env.reset()
    env.step("answer:wrong")
    try:
        env.step("search_project")
    except RuntimeError as exc:
        assert "terminated" in str(exc)
    else:
        raise AssertionError("terminal episode should reject more actions")
