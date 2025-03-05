from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import os

@dataclass
class ResearchResult:
    query: str
    summary: str
    sources: List[Dict[str, Any]]
    subqueries: List[str]
    depth: int
    content_analysis: Optional[List[Dict[str, Any]]] = None
    chain_of_thought: Optional[List[str]] = None
    research_stats: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_markdown(self, include_chain_of_thought: bool=False, include_objective: bool=False) -> str:
        stats = self.research_stats or {}
        elapsed_time = stats.get("elapsed_time_formatted", "Unknown")
        sources_count = stats.get("sources_count", len(self.sources))
        subqueries_count = stats.get("subqueries_count", len(self.subqueries))

        summary = self.summary

        lines = summary.split("\n")


        cleaned_lines = []
        for line in lines:
            if (line.strip().startswith("*Generated on: ") or
                line.strip().startswith("Completed: ") or
                "Here are" in line and ("search queries" in line or "queries to investigate" in line) or
                line.srip() == "Research Framework:" or 
                "Key Findings:" in line or
                "Key aspects to focus on:" in line):
                continue
            cleaned_lines.append(line)
        
        summary = "\n".join(cleaned_lines)

        if summary.startswith("# Research Report: **Objective**"):
            summary = summary.replace("# Research Report: **Objective**", "# Research Report")

        if not include_objective and "**Objective:**" in summary:
            parts = summary.split("##")
            filtered_parts = []

            for part in parts:
                if part.startswith("Executive Summary") or not part.strip():
                    filtered_parts.append(part)
                    continue

                if "**Objective:**" in part and "**Key Aspects to Focus On:**" in part:
                    continue

                filtered_parts.append(part)
            
            if filtered_parts:
                if not filtered_parts[0].startswith("Executive Summary"):
                    filtered_parts.insert(0, "## Executive Summary")
