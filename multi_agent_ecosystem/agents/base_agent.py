import json
from abc import ABC, abstractmethod
from typing import Any
import anthropic
from multi_agent_ecosystem.assessment.self_assessor import SelfAssessor, AssessmentResult
from multi_agent_ecosystem.memory.shared_memory import SharedMemory


class AgentResult:
    def __init__(self, output: str, assessment: AssessmentResult | None = None):
        self.output = output
        self.assessment = assessment

    def __repr__(self) -> str:
        score = self.assessment.score if self.assessment else "N/A"
        return f"AgentResult(score={score}, output={self.output[:80]!r})"


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = "You are a helpful AI agent."
    max_retries: int = 3

    def __init__(
        self,
        api_key: str | None = None,
        memory: SharedMemory | None = None,
        assessor: SelfAssessor | None = None,
        min_score: int = 7,
    ):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.memory = memory
        self.assessor = assessor or SelfAssessor(api_key=api_key)
        self.min_score = min_score

    @property
    @abstractmethod
    def tools(self) -> list[dict]:
        """Return list of Claude tool definitions."""

    @abstractmethod
    def dispatch_tool(self, tool_name: str, tool_input: dict) -> Any:
        """Execute a tool call and return the result."""

    async def run(self, task: str) -> AgentResult:
        """Run agent with self-assessment retry loop."""
        current_task = task
        last_result = None

        for attempt in range(self.max_retries):
            output = self._run_tool_loop(current_task)
            assessment = await self.assessor.assess(task=task, output=output, min_score=self.min_score)
            last_result = AgentResult(output=output, assessment=assessment)

            if self.memory:
                await self.memory.store(
                    key=f"{self.name}:last_result",
                    value=output,
                    agent=self.name,
                )

            if assessment.passed:
                return last_result

            current_task = (
                f"{task}\n\n"
                f"Previous attempt (score {assessment.score}/10):\n{output}\n\n"
                f"Feedback: {assessment.feedback}\n"
                f"Please improve your response."
            )

        return last_result

    def _run_tool_loop(self, task: str) -> str:
        messages = [{"role": "user", "content": task}]

        while True:
            response = self.client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            if response.stop_reason == "end_turn":
                text_blocks = [b.text for b in response.content if hasattr(b, "text")]
                return "\n".join(text_blocks)

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = self.dispatch_tool(block.name, block.input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop reason — return whatever text we have
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(text_blocks) or "No output produced."
