import pytest
from examples.score_centering_demo import decompose


def test_expected_score_under_sampler_is_q_minus_p():
    assert decompose(0.6, 0.8, 1.5, -0.5)["mean_score"] == pytest.approx(0.2)


def test_naive_update_equals_drift_plus_signal():
    result=decompose(0.6, 0.8, 1.5, -0.5)
    assert result["naive"] == pytest.approx(result["drift"] + result["signal"])


def test_score_centering_keeps_covariance_signal():
    result=decompose(0.6, 0.8, 1.5, -0.5)
    assert result["centered"] == pytest.approx(result["signal"])


def test_constant_advantage_has_zero_centered_expected_update():
    result=decompose(0.6, 0.8, 1.0, 1.0)
    assert result["signal"] == pytest.approx(0.0)
    assert result["centered"] == pytest.approx(0.0)


def test_on_policy_centering_is_a_noop():
    result=decompose(0.63, 0.63, 1.5, -0.5)
    assert result["mean_score"] == pytest.approx(0.0)
    assert result["drift"] == pytest.approx(0.0)
    assert result["centered"] == pytest.approx(result["naive"])


@pytest.mark.parametrize("p,q", [(0.2,0.8),(0.8,0.2),(0.5,0.5)])
def test_centered_score_mean_is_zero(p,q):
    s1,s0=1-p,-p
    mean=q*s1+(1-q)*s0
    assert q*(s1-mean)+(1-q)*(s0-mean) == pytest.approx(0.0)


def test_invalid_probabilities_are_rejected():
    with pytest.raises(ValueError): decompose(0.0,0.5,1.0,0.0)
    with pytest.raises(ValueError): decompose(0.5,1.0,1.0,0.0)
