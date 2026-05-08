import json
import re
import anthropic
from pydantic import BaseModel, computed_field


DEFAULT_MIN_SCORE = 7


class AssessmentResult(BaseModel):
    score: int
    feedback: str
    min_score: int = DEFAULT_MIN_SCORE

    @computed_field
    @property
    def passed(self) -> bool:
        return self.score >= self.min_score


class SelfAssessor:
    def __init__(self, api_key: str | None = None, min_score: int = DEFAULT_MIN_SCORE):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.default_min_score = min_score

    async def assess(
        self, task: str, output: str, min_score: int | None = None
    ) -> AssessmentResult:
        threshold = min_score if min_score is not None else getattr(self, 'default_min_score', DEFAULT_MIN_SCORE)
        result = await self._call_claude(task, output)
        return AssessmentResult(score=result.score, feedback=result.feedback, min_score=threshold)

    async def _call_claude(self, task: str, output: str) -> AssessmentResult:
        prompt = f"""You are evaluating an AI agent's output.

Task given to agent:
{task}

Agent's output:
{output}

Score the output from 1-10 (10 = perfect, 1 = completely wrong/useless).
Respond with ONLY valid JSON in this exact format:
{{"score": <integer 1-10>, "feedback": "<one sentence explaining the score>"}}"""

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        if not response.content:
            return AssessmentResult(score=1, feedback="Claude returned no content.")
        text = response.content[0].text.strip()
        match = re.search(r'\{.*\}', text, re.DOTALL)
        try:
            data = json.loads(match.group(0) if match else text)
            score = max(1, min(10, int(data["score"])))
            return AssessmentResult(score=score, feedback=str(data["feedback"]))
        except (json.JSONDecodeError, KeyError, ValueError):
            return AssessmentResult(score=1, feedback=f"Failed to parse assessment response: {text[:100]}")
