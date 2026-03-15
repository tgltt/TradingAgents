from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import ChatGenerationChunk, GenerationChunk, LLMResult
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage

from tenacity import RetryCallState

import logging
from tradingagents.log.log import TRADING_AGENTS_GRAPH
tag_logger = logging.getLogger(TRADING_AGENTS_GRAPH)

class LogCallBackHandler(BaseCallbackHandler):
    
    def on_chat_model_start(
        self,
        serialized: dict[str, Any],
        messages: list[list[BaseMessage]],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"on_chat_model_start, serialized={serialized}, messages={messages}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")

    
    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"on_llm_start, serialized={serialized}, prompts={prompts}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")
    

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"on_llm_end, response={response}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, kwargs={kwargs}")
    

    def on_llm_new_token(
        self,
        token: str,
        *,
        chunk: GenerationChunk | ChatGenerationChunk | None = None,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_llm_new_token, token={token}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, kwargs={kwargs}")
        

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_llm_error, error={error}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}， kwargs={kwargs}")
    

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_chain_start, serialized={serialized}, inputs={inputs}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")
        
        
    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_chain_end, outputs={outputs}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")


    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_chain_error, error={error}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")
    

    def on_agent_action(
        self,
        action: AgentAction,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_agent_action, action={action}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")
    

    def on_agent_finish(
        self,
        finish: AgentFinish,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_agent_finish, finish={finish}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")
 
 
    def on_tool_start(
        self,
        serialized: dict[str, Any],
        input_str: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        inputs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_tool_start, input_str={input_str}, serialized={serialized}, inputs={inputs}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")
           
        
    def on_tool_end(
        self,
        output: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_tool_end, output={output}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")


    def on_tool_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_tool_error, error={error}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")


    def on_retriever_start(
        self,
        serialized: dict[str, Any],
        query: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_retriever_start, query={query}, serialized={serialized}, run_id={run_id}, parent_run_id={parent_run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")
    
        
    def on_text(
        self,
        text: str,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_text, text={text}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")
    

    def on_retry(
        self,
        retry_state: RetryCallState,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_retry, retry_state={retry_state}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")
    

    def on_custom_event(
        self,
        name: str,
        data: Any,
        *,
        run_id: UUID,
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        tag_logger.debug(f"---> on_custom_event, name={name}, data={data}, run_id={run_id}, tags={tags}, metadata={metadata}, kwargs={kwargs}")