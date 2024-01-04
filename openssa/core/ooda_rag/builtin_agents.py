from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
import json
from loguru import logger
from openssa.core.ooda_rag.prompts import BuiltInAgentPrompt
from openssa.utils.utils import Utils
from openssa.utils.llms import OpenAILLM, AnLLM


class AgentRole:
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class TaskAgent(ABC):
    """
    Abstract base class for all task agents.
    """

    @abstractmethod
    def execute(self, task: str) -> str:
        """
        Execute the task agent with the given task.
        """
        pass


class AskUserAgent(TaskAgent):
    """
    AskUserAgent helps to determine if user wants to provide additional information
    """

    def __init__(
        self,
        llm: AnLLM = OpenAILLM.get_gpt_4_1106_preview(),
        ask_user_heuristic: str = "",
        conversation: Optional[List] = None,
    ) -> None:
        self.llm = llm
        self.ask_user_heuristic = ask_user_heuristic.strip()
        self.conversation = conversation[-10:] if conversation else []

    @Utils.timeit
    def execute(self, task: str = "") -> str:
        if not self.ask_user_heuristic:
            return ""
        system_message = {
            "role": AgentRole.SYSTEM,
            "content": BuiltInAgentPrompt.ASK_USER.format(
                problem_statement=task,
                heuristic=self.ask_user_heuristic,
            ),
        }
        conversation = self.conversation + [system_message]
        response = self.llm.call(
            messages=conversation,
            response_format={"type": "json_object"},
        )
        json_str = response.choices[0].message.content
        logger.debug(f"ask user response is: {json_str}")
        try:
            jobject = json.loads(json_str)
            return jobject.get("question", "")
        except json.JSONDecodeError:
            logger.error("Failed to decode the response as JSON for ask user agent.")
            return ""


class GoalAgent(TaskAgent):
    """
    GoalAgent helps to determine problem statement from the conversation between user and SSA
    """

    def __init__(
        self,
        llm: AnLLM = OpenAILLM.get_gpt_4_1106_preview(),
        conversation: Optional[List] = None,
    ) -> None:
        self.llm = llm
        self.conversation = conversation[-10:] if conversation else []

    @Utils.timeit
    def execute(self, task: str = "") -> str:
        system_message = {
            "role": AgentRole.SYSTEM,
            "content": BuiltInAgentPrompt.PROBLEM_STATEMENT,
        }
        conversation = self.conversation + [system_message]
        response = self.llm.call(
            messages=conversation,
            response_format={"type": "json_object"},
        )
        json_str = response.choices[0].message.content
        logger.debug(f"problem statement response is: {json_str}")
        try:
            jobject = json.loads(json_str)
            return jobject.get("problem statement", "")
        except json.JSONDecodeError:
            logger.error("Failed to decode the response as JSON for goal agent.")
            return conversation[-1].get("content", "")


class ContextValidator(TaskAgent):
    """
    ContentValidatingAgent helps to determine whether the content is sufficient to answer the question
    """

    def __init__(
        self,
        llm: AnLLM = OpenAILLM.get_gpt_4_1106_preview(),
        conversation: Optional[List] = None,
        context: Optional[list] = None,
    ) -> None:
        self.llm = llm
        self.conversation = conversation[-10:-1] if conversation else []
        self.context = context

    @Utils.timeit
    def execute(self, task: str = "") -> dict:
        system_message = {
            "role": "system",
            "content": BuiltInAgentPrompt.CONTENT_VALIDATION.format(
                context=self.context, query=task
            ),
        }
        conversation = self.conversation + [system_message]
        response = self.llm.call(
            messages=conversation,
            response_format={"type": "json_object"},
        )
        json_str = response.choices[0].message.content
        try:
            jobject = json.loads(json_str)
        except json.JSONDecodeError:
            logger.error(
                "Failed to decode the response as JSON for content validation agent."
            )
            return {}

        return jobject


class SynthesizingAgent(TaskAgent):
    """
    SynthesizeAgent helps to synthesize answer
    """

    def __init__(
        self,
        llm: AnLLM = OpenAILLM.get_gpt_4_1106_preview(),
        conversation: Optional[List] = None,
        context: Optional[list] = None,
    ) -> None:
        self.llm = llm
        self.conversation = conversation[-10:-1] if conversation else []
        self.context = context

    @Utils.timeit
    def execute(self, task: str = "") -> dict:
        system_message = {
            "role": "system",
            "content": BuiltInAgentPrompt.SYNTHESIZE_RESULT.format(
                context=self.context, query=task
            ),
        }
        conversation = self.conversation + [system_message]
        response = self.llm.call(
            messages=conversation,
            response_format={"type": "json_object"},
        )
        json_str = response.choices[0].message.content
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error(
                "Failed to decode the response as JSON for content validation agent."
            )
            return {}


class OODAPlanAgent(TaskAgent):
    """
    OODAPlanAgent helps to determine the OODA plan from the problem statement
    """

    def __init__(
        self,
        llm: AnLLM = OpenAILLM.get_gpt_4_1106_preview(),
        conversation: Optional[List] = None,
    ) -> None:
        self.llm = llm
        self.conversation = conversation[-10:] if conversation else []

    @Utils.timeit
    def execute(self, task: str = "") -> dict:
        system_message = {
            "role": "system",
            "content": BuiltInAgentPrompt.GENERATE_OODA_PLAN,
        }
        conversation = self.conversation + [system_message]
        response = self.llm.call(
            messages=conversation,
            response_format={"type": "json_object"},
        )
        json_str = response.choices[0].message.content
        logger.debug(f"OODA plan response is: {json_str}")
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error("Failed to decode the response as JSON for OODA plan agent.")
            return {}
