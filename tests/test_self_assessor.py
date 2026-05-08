import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from multi_agent_ecosystem.assessment.self_assessor import SelfAssessor, AssessmentResult

@pytest.mark.asyncio
async def test_high_score_passes():
    assessor = SelfAssessor.__new__(SelfAssessor)
    assessor._call_claude = AsyncMock(return_value=AssessmentResult(score=9, feedback="Excellent output"))
    result = await assessor.assess(task="Write hello world", output="print('hello world')")
    assert result.score == 9
    assert result.passed is True

@pytest.mark.asyncio
async def test_low_score_fails():
    assessor = SelfAssessor.__new__(SelfAssessor)
    assessor._call_claude = AsyncMock(return_value=AssessmentResult(score=4, feedback="Output incomplete"))
    result = await assessor.assess(task="Write hello world", output="pass")
    assert result.score == 4
    assert result.passed is False

@pytest.mark.asyncio
async def test_threshold_is_configurable():
    assessor = SelfAssessor.__new__(SelfAssessor)
    assessor._call_claude = AsyncMock(return_value=AssessmentResult(score=6, feedback="Decent"))
    result = await assessor.assess(task="task", output="output", min_score=5)
    assert result.passed is True

@pytest.mark.asyncio
async def test_assessment_result_model():
    result = AssessmentResult(score=7, feedback="Good work")
    assert result.score == 7
    assert result.feedback == "Good work"
    assert result.passed is True  # default threshold = 7
