from typing import List, Optional, Dict, Any, Callable
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.base import BaseCallbackHandler
from config import config
from src.utils.langsmith import setup_langsmith_tracing
from src.topic.manager import TopicManager


class ToolCallLimitCallback(BaseCallbackHandler):
    """Callback to track and limit tool calls"""
    
    def __init__(self, max_calls: int, permission_callback: Optional[Callable] = None):
        """
        Initialize the callback.
        
        Args:
            max_calls: Maximum number of tool calls allowed
            permission_callback: Function to call when limit reached, should return bool
        """
        super().__init__()
        self.tool_call_count = 0
        self.max_calls = max_calls
        self.permission_callback = permission_callback
        self.permission_granted = True
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs) -> None:
        """Called when a tool is about to be used"""
        self.tool_call_count += 1
        
        # Check if approaching limit (80% threshold)
        if self.tool_call_count >= int(self.max_calls * 0.8):
            print(f"\n⚠️  Tool call {self.tool_call_count}/{self.max_calls} - approaching limit")
        
        # Check if limit reached
        if self.tool_call_count >= self.max_calls:
            if self.permission_callback:
                self.permission_granted = self.permission_callback(self.tool_call_count)
                if not self.permission_granted:
                    raise Exception(
                        f"Tool call limit ({self.max_calls}) reached. "
                        "User denied permission to continue."
                    )
            else:
                print(f"\n🛑 Tool call limit ({self.max_calls}) reached!")
    
    def on_tool_error(self, error: Exception, **kwargs) -> None:
        """Called when a tool encounters an error"""
        print(f"\n⚠️  Tool error: {str(error)}")
    
    def on_tool_end(self, output: str, **kwargs) -> None:
        """Called when a tool completes successfully"""
        pass
    
    def reset(self):
        """Reset the counter"""
        self.tool_call_count = 0
        self.permission_granted = True


class ResearchAgent:
    """
    LangChain ReAct agent for autonomous AI research.
    
    This agent uses the ReAct (Reasoning and Acting) pattern to autonomously
    search the web, manage memory, and generate reports.
    """
    
    def __init__(
        self,
        tools: List[BaseTool],
        verbose: bool = True,
        use_memory: bool = True,
        permission_callback: Optional[Callable] = None,
        enable_langsmith: bool = True,
        topic_manager: Optional[TopicManager] = None
    ):
        """
        Initialize the research agent.

        Args:
            tools: List of LangChain tools available to the agent
            verbose: Whether to print agent reasoning steps
            use_memory: Whether to use conversation memory for context
            permission_callback: Function to call when tool limit reached
            enable_langsmith: Whether to enable LangSmith tracing
            topic_manager: TopicManager instance for topic-aware prompts
        """
        self.tools = tools
        self.verbose = verbose
        self.max_tool_calls = config.MAX_TOOL_CALLS
        self.use_memory = use_memory
        self.permission_callback = permission_callback
        self.topic_manager = topic_manager
        
        # Setup LangSmith tracing
        self.langsmith_client = None
        if enable_langsmith:
            self.langsmith_client = setup_langsmith_tracing()
        
        # Initialize tool call limit callback
        self.tool_limit_callback = ToolCallLimitCallback(
            max_calls=self.max_tool_calls,
            permission_callback=permission_callback
        )
        
        # Initialize conversation memory
        self.memory = None
        if use_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="output"
            )
        
        # Initialize LLM based on provider
        if config.LLM_PROVIDER == "openrouter":
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                api_key=config.OPENROUTER_API_KEY,
                base_url=config.OPENROUTER_BASE_URL,
            )
        else:  # Default to OpenAI
            self.llm = ChatOpenAI(
                model=config.LLM_MODEL,
                temperature=config.LLM_TEMPERATURE,
                api_key=config.OPENAI_API_KEY,
            )
        
        # Create ReAct prompt
        self.prompt = self._create_react_prompt()
        
        # Create ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        )
        
        # Create agent executor with optional memory
        executor_kwargs = {
            "agent": self.agent,
            "tools": self.tools,
            "verbose": self.verbose,
            "handle_parsing_errors": True,
            "max_iterations": self.max_tool_calls,
        }
        
        if self.memory:
            executor_kwargs["memory"] = self.memory
        
        self.agent_executor = AgentExecutor(**executor_kwargs)
    
    def _create_react_prompt(self) -> PromptTemplate:
        """
        Create the ReAct prompt template for the agent.

        Returns:
            PromptTemplate configured for ReAct reasoning
        """
        # Get topic context from topic manager
        if self.topic_manager:
            context = self.topic_manager.get_domain_prompt_context()
            domain = context["domain"]
            description = context["description"]
            keywords = context["keywords"]
            focus_areas = context["focus_areas"]
        else:
            # Fallback to AI/ML
            domain = "AI/ML"
            description = "AI and Machine Learning development"
            keywords = "AI libraries, ML frameworks, LLM models, vector databases"
            focus_areas = "new libraries, frameworks, models, and tools"

        template = f"""You are a Research Assistant specialized in tracking trending topics in {description}.

Your mission is to research {focus_areas} in the {domain} ecosystem. You have access to tools to search the web, check your memory for previously researched topics, save findings to memory, and send email reports.

RESEARCH FOCUS:
- Domain: {domain}
- Key areas: {keywords}
- Focus on: {focus_areas}

IMPORTANT MEMORY WORKFLOW:
1. BEFORE researching: Use check_memory or check_novelty to see if the topic was already researched
2. DURING research: Gather information using search tools
3. AFTER researching: Use save_to_memory to store your findings so you don't repeat them later
4. Only present novel information that hasn't been shared in the last 7 days

SAVING TO MEMORY:
After researching a topic, ALWAYS save it to memory with:
- Topic name
- Brief summary of what you found
- Source URLs you used
- Relevant tags

This ensures you won't waste time re-researching the same topics.

SENDING NEWSLETTERS:
When the user asks for a newsletter:
1. Use send_research_newsletter tool with the number of topics to include
2. The tool will retrieve findings and send the email automatically
3. Done!

Example workflow:
User: "Send me a newsletter"
1. Call send_research_newsletter with number of topics (e.g., "10")
2. Done! The newsletter will be retrieved and emailed automatically

TOOLS:
You have access to the following tools:

{{tools}}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{{tool_names}}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {{input}}
Thought: {{agent_scratchpad}}"""

        return PromptTemplate(
            template=template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools]),
                "tool_names": ", ".join([tool.name for tool in self.tools]),
            }
        )
    
    def run(self, query: str, run_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent with a query.
        
        Args:
            query: The user's question or command
            run_name: Optional name for the LangSmith run
            
        Returns:
            Dictionary containing the agent's response and metadata
        """
        try:
            # Configure callbacks and metadata for LangSmith
            run_config = {
                "callbacks": [self.tool_limit_callback],
            }
            
            # Add LangSmith metadata if enabled
            if self.langsmith_client:
                run_config["run_name"] = run_name or "research_agent_run"
                run_config["tags"] = ["research", "agent", "react"]
                run_config["metadata"] = {
                    "query": query[:100],  # First 100 chars
                    "max_tool_calls": self.max_tool_calls,
                }
            
            result = self.agent_executor.invoke(
                {"input": query},
                config=run_config
            )
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
        except KeyboardInterrupt:
            # Handle user interruption gracefully
            return {
                "success": False,
                "error": "Interrupted by user",
                "output": "Execution interrupted by user.",
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
        except Exception as e:
            # Log error details for debugging
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if "rate limit" in error_msg.lower():
                output = "⚠️ API rate limit reached. Please try again in a moment."
            elif "timeout" in error_msg.lower():
                output = "⚠️ Request timed out. Please check your connection and try again."
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                output = "⚠️ Authentication error. Please check your API keys in .env file."
            elif "tool call limit" in error_msg.lower():
                output = f"🛑 {error_msg}"
            else:
                output = f"⚠️ An error occurred: {error_msg}"
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "output": output,
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
    
    async def arun(self, query: str, run_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the agent asynchronously with a query.
        
        Args:
            query: The user's question or command
            run_name: Optional name for the LangSmith run
            
        Returns:
            Dictionary containing the agent's response and metadata
        """
        try:
            # Configure callbacks and metadata for LangSmith
            run_config = {
                "callbacks": [self.tool_limit_callback],
            }
            
            # Add LangSmith metadata if enabled
            if self.langsmith_client:
                run_config["run_name"] = run_name or "research_agent_run_async"
                run_config["tags"] = ["research", "agent", "react", "async"]
                run_config["metadata"] = {
                    "query": query[:100],  # First 100 chars
                    "max_tool_calls": self.max_tool_calls,
                }
            
            result = await self.agent_executor.ainvoke(
                {"input": query},
                config=run_config
            )
            return {
                "success": True,
                "output": result.get("output", ""),
                "intermediate_steps": result.get("intermediate_steps", []),
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
        except KeyboardInterrupt:
            # Handle user interruption gracefully
            return {
                "success": False,
                "error": "Interrupted by user",
                "output": "Execution interrupted by user.",
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
        except Exception as e:
            # Log error details for debugging
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if "rate limit" in error_msg.lower():
                output = "⚠️ API rate limit reached. Please try again in a moment."
            elif "timeout" in error_msg.lower():
                output = "⚠️ Request timed out. Please check your connection and try again."
            elif "api key" in error_msg.lower() or "authentication" in error_msg.lower():
                output = "⚠️ Authentication error. Please check your API keys in .env file."
            elif "tool call limit" in error_msg.lower():
                output = f"🛑 {error_msg}"
            else:
                output = f"⚠️ An error occurred: {error_msg}"
            
            return {
                "success": False,
                "error": error_msg,
                "error_type": error_type,
                "output": output,
                "tool_calls": self.tool_limit_callback.tool_call_count,
            }
    
    def reset_tool_call_count(self):
        """Reset the tool call counter"""
        self.tool_limit_callback.reset()
    
    def get_tool_call_count(self) -> int:
        """Get the current tool call count"""
        return self.tool_limit_callback.tool_call_count
    
    def check_tool_call_limit(self) -> bool:
        """
        Check if the tool call limit has been reached.
        
        Returns:
            True if limit reached, False otherwise
        """
        return self.tool_limit_callback.tool_call_count >= self.max_tool_calls
    
    def clear_memory(self):
        """Clear conversation memory"""
        if self.memory:
            self.memory.clear()
    
    def get_memory_context(self) -> List[Any]:
        """
        Get the current conversation context from memory.
        
        Returns:
            List of messages in the conversation history
        """
        if self.memory:
            return self.memory.load_memory_variables({}).get("chat_history", [])
        return []
