from typing import List, Dict, Any, Callable, Union, TypedDict, Sequence, Optional
from dataclasses import dataclass
import time
import re
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from ..processors.content_processor import AgentState

console = Console()

def get_user_input(prompt: str) -> str:
    console.print(prompt, style="yellow")
    return input("> ").strip()

def should_continue(state: AgentState) -> str:
    if state["current_depth"] < state["depth"]:
        return "continue"
    return "end"

def log_chain_of_thought(state: AgentState, thought: str) -> None:
    timestamp = datetime.now().strftime("%H:%M:%S")
    state["chain_of_thought"].append(f"{timestamp}: {thought}")

def display_research_progress(state: AgentState) -> None:
    elapsed_time = time.time() - state["start_time"]
    minutes, seconds = divmod(elapsed_time, 60)
    status = state["status"]
    pharse = "Research" if "depth" in state.lower() or any(word in state.lower() for word in ["searching", "querying", "reflecting", "analyzing"]) else "Report Generation"

    tree = Tree(f"[bold blue]{pharse} Progress: {status}")

    stats_node = tree.add(f"[cyan]Stats")
    stats_node.add(f"[blue]Time Elapsed:[/] {minutes}m {seconds}s")

    if pharse == "Research":
        stats_node.add(f"[blue]Current Depth:[/] {state['current_depth']}/{state['depth']}")
        stats_node.add(f"[blue]Sources Found:[/] {len(state['sources'])}")
        stats_node.add(f"[blue]Subqueries Explored:[/] {len(state['subqueries'])}")

        if state['subqueries']:
            queries_node = tree.add(f"[green]Current Research Paths")
            for query in state['subqueries'][-state['breadth']]:
                queries_node.add(query)
    else:
        stats_node.add(f"[blue]Sources Selected:[/] {len(state.get('selected_sources', []))}")

        report_progress = tree.add("[green]Report Generation Progreses")
        if state.get("selected_sources"):
            report_progress.add(f"[green]✓[green] Sources selected")
        if state.get("formatted_citations"):
            report_progress.add(f"[green]✓[green] Citations formatted")
        if state.get("initial_report"):
            report_progress.add(f"[green]✓[green] Initial report generated")
        if state.get("enhanced_report"):
            report_progress.add(f"[green]✓[green] Report enhanced with details")
        if state.get("final_report"):
            report_progress.add(f"[green]✓[green] Key sections expanded")
    
    if state["chain_of_thought"]:
        thoughts_node = tree.add("[yellow]Recent Thoughts")
        for thought in state["chain_of_thought"][-3:]:
            thoughts_node.add(thought)
        
    if pharse == "Research" and state["findings"]:
        findings_node = tree.add("[magenta]Latest Findings")
        sections = state["findings"].split("\n\n")
        for section in sections[-2:]:
            if section.strip():
                findings_node.add(section.strip()[:100] + "..." if len(section.strip()) > 100 else section.strip())
            
    return tree

async def _call_progress_callback(callback: Optional[Callable], state: AgentState) -> None:
    if callback:
        import asyncio
        if asyncio.iscoroutinefunction(callback):
            await callback(state)
        else:
            callback(state)

async def clarify_query(query: str, llm, date: Optional[str] = None, system_prompt: str = "", user_prompt: str = "") -> str:
    from langchain_core.prompts import ChatPromptTemplate

    current_date = date or datetime.now().strftime("%Y-%m-%d")
    console.print(f"[bold blue]Initial Query:[/] {query}")
    console.print(f"[bold]I'll ask a few questions to better understand your research needs.[/]")

    if not system_prompt:
        system_prompt = f"""You are an expert research consultant helping to clarify a research query.
        
        Today is {current_date}
        
        Analyze the given research query and create 3 targeted follow-up questions that will help you better understand:
        1. The specific scope and boundaries of the research
        2. The level of detail and technical depth needed
        3. Any specific perspectives, approaches, or source types preferred

        Ask questions that will reveal what the user REALLY wants to know.
        Format each question on a new line with no numbering or bullets.
        Each question should be standalone and specific.
        """
    if not user_prompt:
        user_prompt = """I need to conduct research on the following topic:
        
        {query}

        Please ask me 3 clarifying questions to better understand what I need.
        """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", user_prompt)
    ])

    chain = prompt | llm
    response = chain.invoke({"query": query})
    questions = [q.strip() for q in response.content.split("\n") if q.strip() and "?" in q]

    answers = []
    for q in questions[:3]:
        answer = get_user_input(q)
        answers.append(answer)
    
    qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])

    refinement_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""You are crafting a refined, comprehensive research query based on an initial query and clarifying Q&A.
        
        Today is {current_date}
        
        Your task is to:
        1. Analyze the initial query and clarifying Q&A
        2. Create a detailed, well-structured research query that captures all the important aspects
        3. Format the query as a clear, specific research question or directive
        4. DO NOT include phrases likee "Based on our disscussion" or similar meta-commentary
        5. DO NOT include section headings like "Research Framework" or "Refined Query"
        
        The output should be ONLY the refined query text, nothing else.
        """),
        ("user", f"""Initial query: {query}
        
        Clarifying Q&A:
        {qa_text}
        
        Based on this information, create a comprehensive, well-structured research query.
        """)
    ])

    refined_query = refinement_prompt | llm
    refined_context_raw = refined_query.invoke({"query": query, "qa": qa_text}).content

    refined_context = refined_context_raw.replace("**", "").replace("# ", "").replace("## ", "")
    refined_context = re.sub(r"^(?:Based on our discussion, |Following our converstation, |As per our discussion,).*?(?:refined topic:|research the following:|exploring|analyze):\s*", '', refined_context, flags=re.IGNORECASE)
    refined_context = re.sub(r'Based on our discussion.*?(?=\.)\.', '', refined_context, flags=re.IGNORECASE)

    console.print(f"\n[bold green]Refined Research Query:[/]{refined_context}")
    return refined_context