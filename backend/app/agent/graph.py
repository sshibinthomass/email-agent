from langgraph.graph import START, END

from pathlib import Path
import sys

current_file = Path(__file__).resolve()
project_root = current_file.parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.agent.nodes import EmailClassifierNode

def email_classifier_build_graph(graph_builder, llm):
    """
    Builds a basic chatbot graph using LangGraph.
    This method initializes a chatbot node using the `BasicChatbotNode` class
    and integrates it into the graph. The chatbot node is set as both the
    entry and exit point of the graph.

    Args:
        graph_builder: The StateGraph instance to add nodes to
        llm: The language model to use for the chatbot
    """
    email_classifier_node = EmailClassifierNode(llm)

    graph_builder.add_node("email_classifier", email_classifier_node.process)
    graph_builder.add_edge(START, "email_classifier")
    graph_builder.add_edge("email_classifier", END)
