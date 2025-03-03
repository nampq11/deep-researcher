import time
import asyncio
from datetime import datetime
from typing import List, Dict, Optional, Any, Callable
from langchain_together.chat_models import ChatTogether
from langchain_core.messages import HumanMessage
from rich.console import Console
from rich.panel import Panel
from ..config import config, get_current_date

console = Console()


class ResearchGraph:
    def __init__(
        self,
        llm: Optional[ChatTogether] = None,
        searcher: Optional[Callable] = None,
        temperature: float = 0.5,
        date: Optional[str] = None,
    ):
        api_key = config.get("api", "api_key")
        model = config.get("api", "model")

        self.llm = llm or ChatTogether(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=16384,
        )

    def _build_graph(self):
        """Build the research graph."""
    
        