from langgraph.graph import Graph, StateGraph

def build_graph(
    initialize_node,
    reflect_node,
    generate_queries_node,
    search_node,
    smart_source_selection,
    format_citations_node,
    generate_initial_report_node,
    enhance_report_node,
    expand_key_sections_node,
    report_node
) -> Graph:
    """
    Building the research workflow graph with all nodes.

    Args:
        Compiled graph ready for execution
    """
    workflow = StateGraph()
    