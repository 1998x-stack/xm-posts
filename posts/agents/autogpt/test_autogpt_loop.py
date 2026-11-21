from autogpt_loop import PlannedAction, run_plan


def sample_plan():
    return [
        PlannedAction("search_sources", "read", "找到三篇候选资料"),
        PlannedAction("write_draft", "workspace", "草稿已写入工作区"),
        PlannedAction("publish", "external", "页面已发布", goal_complete=True),
    ]


def test_external_action_is_blocked_without_approval():
    result = run_plan("整理并发布研究摘要", sample_plan(), max_steps=5)
    assert not result.completed
    assert result.stop_reason == "approval_required"
    assert result.trace[-1].status == "blocked"
    assert result.trace[-1].action == "publish"


def test_external_action_runs_only_after_explicit_approval():
    result = run_plan(
        "整理并发布研究摘要",
        sample_plan(),
        max_steps=5,
        approved_external={"publish"},
    )
    assert result.completed
    assert result.stop_reason == "goal_complete"
    assert [entry.status for entry in result.trace] == [
        "executed", "executed", "executed"
    ]


def test_step_budget_stops_before_unstarted_action():
    result = run_plan("完成任务", sample_plan(), max_steps=1)
    assert not result.completed
    assert result.stop_reason == "budget_exhausted"
    assert len(result.trace) == 1


def test_tool_error_is_recorded_and_stops_the_plan():
    plan = [
        PlannedAction("search", "read", "temporary error", succeeds=False),
        PlannedAction("publish", "external", "published", goal_complete=True),
    ]
    result = run_plan("完成任务", plan, approved_external={"publish"})
    assert not result.completed
    assert result.stop_reason == "tool_error"
    assert result.trace[0].status == "error"


def test_empty_goal_and_negative_budget_are_rejected():
    import pytest

    with pytest.raises(ValueError):
        run_plan(" ", sample_plan())
    with pytest.raises(ValueError):
        run_plan("task", sample_plan(), max_steps=-1)
