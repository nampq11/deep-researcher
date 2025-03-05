from typing import List, Dict, TypedDict, Sequence, Union, Any
from langchain_core.messages import AIMessage, HumanMessage, BaseMessage
from langchain_together.chat_models import ChatTogether
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class AgentState(TypedDict):
    messages: Sequence[Union[HumanMessage, AIMessage]]
    query: str
    depth: str
    breadth: str
    current_depth: int
    findings: str
    sources: List[Dict[str, Any]]
    selected_sources: List[str]
    formatted_citations: str
    subqueries: List[str]
    content_analysis: Dict[str, Any]
    start_time: float
    chain_of_thought: List[str]
    status: str
    current_date: str
    detail_level: str
    indentified_themes: str
    initial_report: str
    enhanced_report: str
    final_report: str

async def is_relevant_url(llm: ChatTogether, url: str, title: str, snippet: str, query: str) -> bool:
    irrelevant_domains = ["pinterest", "instagram", "facebook", "twitter"]

    if any(domain in url.lower() for domain in irrelevant_domains):
        return False
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are evaluating search results for relevance to specific query.
        
        DETERMINE if the search result is RELEVANT or NOT RELEVANT to answering the query.
        
        Output ONLY "RELEVANT" or "NOT RELEVANT" based on your analysis.
        """),
        ("user", """Query: {query}
        
        Search Result:
        Title: {title}
        URL: {url}
        Snippet: {snippet}
        
        Is this result relevant to the query? Answer with ONLY "RELEVANT" or "NOT RELEVANT".
        """)
    ])
    chain = prompt | llm | StrOutputParser()
    result = await chain.invoke({"query": query, "title": title, "url": url, "snippet": snippet})
    return "RELEVANT" in result.upper()