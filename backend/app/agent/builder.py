from langgraph.graph import StateGraph

from pathlib import Path
import sys
import dotenv

current_file = Path(__file__).resolve()
project_root = current_file.parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from backend.app.agent.state import AgentState
from backend.app.agent.graph import email_classifier_build_graph

from langgraph.checkpoint.memory import MemorySaver

dotenv.load_dotenv()

# Global checkpointer instance for state/history persistence
memory_checkpointer = MemorySaver()


class GraphBuilder:
    def __init__(self, model):
        self.llm = model
        self.graph_builder = StateGraph(
            AgentState
        )  # StateGraph is a class in LangGraph that is used to build the graph

    async def setup_graph(self, usecase: str):
        """
        Sets up the graph for the selected use case.

        Args:
            usecase: The use case to set up ("basic_chatbot")
        """

        email_classifier_build_graph(self.graph_builder, self.llm)
        return self.graph_builder.compile(checkpointer=memory_checkpointer)


if __name__ == "__main__":
    import asyncio
    from backend.app.agent.llms.openai_llm import OpenAILLM
    from langchain_core.messages import HumanMessage, SystemMessage
    import os

    async def main():
        user_controls_input = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "selected_llm": "gpt-4.1-mini",
        }
        llm = OpenAILLM(user_controls_input)
        llm = llm.get_base_llm()

        graph_builder = GraphBuilder(llm)


        # Setup graph with tools
        graph = await graph_builder.setup_graph("basic_chatbot")

        # Create input state for the graph
        initial_state = {
            "subject": "Anniversary Special: Buy one get one free",
            "body": "As our loyal customer, get exclusive $60 off $75+: example.com/6058 Offer code: WELCOME20.",
            "category": None,
            "reason": None,
            "JudgeVerted": None,
            "JudgeReasoning": None,
        }


        # Initialize Langfuse CallbackHandler if credentials are configured
        callbacks = []
        if os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"):
            try:
                from langfuse.langchain import CallbackHandler
                langfuse_handler = CallbackHandler()
                callbacks.append(langfuse_handler)
            except Exception as e:
                print(f"Warning: Could not initialize Langfuse CallbackHandler: {e}")

        # Run the graph and print the output (use ainvoke for async graph with thread config)
        result = await graph.ainvoke(
            initial_state,
            config={
                "configurable": {"thread_id": "cli-test-thread"},
                "callbacks": callbacks
            }
        )
        print("Graph Output:", result)

    # Run the async main function
    import nest_asyncio

    nest_asyncio.apply()
    asyncio.run(main())
