import time
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from langchain_together.chat_models import ChatTogether
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from ..config import config, get_current_date
from .graph.builder import build_graph
from .processors.content_processor import AgentState
from .utils.agent_utils import should_continue
from .nodes.initialize import initialize_node
console = Console()


class ResearchGraph:
    def __init__(
        self,
        llm: Optional[ChatTogether] = None,
        searcher: Optional[Callable] = None,
        temperature: float = 0.5,
        date: Optional[str] = None,
        initialze_node: Optional[Callable] = None,

    ):
        api_key = config.get("api", "api_key")
        model = config.get("api", "model")

        self.llm = llm or ChatTogether(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=16384,
        )

        self.date = date or get_current_date()
        self.detail_level = "high"
        self.progress_callback = None
        self.include_objective = False
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the research graph."""

        # TODO: Implement the node

        return build_graph(
            initialize_node=None,
            reflect_node=None,
            generate_queries_node=None,
            search_node=None,
            smart_source_selection=None,
            format_citations_node=None,
            generate_initial_report_node=None,
            enhance_report_node=None,
            expand_key_sections_node=None,
            report_node=None,
        )
    
    async def research(
        self,
        query: str,
        depth: int = 2,
        breadth: int = 4,
        progress_callback: Optional[Callable[[AgentState], None]] = None,
        include_objective: bool = False,
        detail_level: str = "high",
    ):
        self.progress_callback = progress_callback
        self.include_objective = include_objective
        self.detail_level = detail_level

        state = AgentState(
            messages=[HumanMessage(content=f"Starting research on: {query}")],
            query=query,
            depth=depth,
            breadth=breadth,
            current_depth=0,
            findings="",
            sources=[],
            selected_sources=[],
            formatted_citations="",
            subqueries=[],
            content_analysis=[],
            start_time=time.time(),
            chain_of_thought=[],
            status="Starting",
            current_date=get_current_date(),
            detail_level=detail_level,
            indentified_themes="",
            initial_report="",
            enhanced_report="",
            final_report="",
        )

        final_state = await self.graph.ainvoke(state)

        elapsed_time = time.time() - final_state["start_time"]
        minutes, seconds = divmod(int(elapsed_time), 60)

        return None
    
    def research_sync(
        self,
        query: str,
        depth: int = 2,
        breadth: int = 4,
        progress_callback: Optional[Callable[[AgentState], None]] = None,
        include_objective: bool = False,
        detail_level: str = "high",
    ) -> ResearchResult:
        return asyncio.run(
            self.research(query, depth, breadth, progress_callback, include_objective, detail_level)
        )