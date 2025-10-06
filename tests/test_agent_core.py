import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain.tools import Tool
from src.agent.core import ResearchAgent, ToolCallLimitCallback


@pytest.fixture
def mock_tools():
    """Create mock tools for testing"""
    def search_func(query: str) -> str:
        return f"Search results for: {query}"
    
    def memory_func(query: str) -> str:
        return f"Memory results for: {query}"
    
    return [
        Tool(
            name="search",
            func=search_func,
            description="Search the web for information"
        ),
        Tool(
            name="memory",
            func=memory_func,
            description="Check memory for previous research"
        ),
    ]


@pytest.fixture
def mock_permission_callback():
    """Create a mock permission callback"""
    return Mock(return_value=True)


class TestToolCallLimitCallback:
    """Test the ToolCallLimitCallback class"""
    
    def test_initialization(self):
        """Test callback initialization"""
        callback = ToolCallLimitCallback(max_calls=5)
        assert callback.tool_call_count == 0
        assert callback.max_calls == 5
        assert callback.permission_granted is True
    
    def test_tool_call_counting(self):
        """Test tool call counting"""
        callback = ToolCallLimitCallback(max_calls=5)
        
        # Simulate tool calls
        callback.on_tool_start({}, "test input")
        assert callback.tool_call_count == 1
        
        callback.on_tool_start({}, "test input")
        assert callback.tool_call_count == 2
    
    def test_warning_at_threshold(self, capsys):
        """Test warning when approaching limit"""
        callback = ToolCallLimitCallback(max_calls=5)
        
        # Call 4 times (80% of 5)
        for _ in range(4):
            callback.on_tool_start({}, "test")
        
        captured = capsys.readouterr()
        assert "approaching limit" in captured.out
    
    def test_permission_callback_on_limit(self):
        """Test permission callback is called at limit"""
        permission_mock = Mock(return_value=True)
        callback = ToolCallLimitCallback(max_calls=3, permission_callback=permission_mock)
        
        # Reach the limit
        for _ in range(3):
            callback.on_tool_start({}, "test")
        
        permission_mock.assert_called_once_with(3)
    
    def test_exception_on_permission_denied(self):
        """Test exception when permission is denied"""
        permission_mock = Mock(return_value=False)
        callback = ToolCallLimitCallback(max_calls=2, permission_callback=permission_mock)
        
        callback.on_tool_start({}, "test")
        
        # Should raise exception on limit when permission denied
        with pytest.raises(Exception, match="Tool call limit"):
            callback.on_tool_start({}, "test")
    
    def test_reset(self):
        """Test resetting the callback"""
        callback = ToolCallLimitCallback(max_calls=5)
        
        callback.on_tool_start({}, "test")
        callback.on_tool_start({}, "test")
        assert callback.tool_call_count == 2
        
        callback.reset()
        assert callback.tool_call_count == 0
        assert callback.permission_granted is True


class TestResearchAgent:
    """Test the ResearchAgent class"""
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_initialization(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test agent initialization"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, verbose=True, enable_langsmith=False)
        
        assert agent.tools == mock_tools
        assert agent.verbose is True
        assert agent.use_memory is True
        assert agent.max_tool_calls == 10  # Default from config
        assert agent.tool_limit_callback is not None
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_initialization_with_memory(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test agent initialization with memory enabled"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, use_memory=True, enable_langsmith=False)
        
        assert agent.memory is not None
        assert agent.memory.memory_key == "chat_history"
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_initialization_without_memory(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test agent initialization without memory"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, use_memory=False, enable_langsmith=False)
        
        assert agent.memory is None
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_langsmith_integration(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test LangSmith integration"""
        mock_client = Mock()
        mock_langsmith.return_value = mock_client
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=True)
        
        mock_langsmith.assert_called_once()
        assert agent.langsmith_client == mock_client
    
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    @patch('src.agent.core.AgentExecutor')
    def test_run_success(self, mock_executor_class, mock_create_agent, mock_chatgpt, mock_langsmith, mock_tools):
        """Test successful agent run"""
        mock_langsmith.return_value = None
        
        # Setup mock executor
        mock_executor = Mock()
        mock_executor.invoke.return_value = {
            "output": "Test response",
            "intermediate_steps": []
        }
        mock_executor_class.return_value = mock_executor
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        result = agent.run("Test query")
        
        assert result["success"] is True
        assert result["output"] == "Test response"
        assert "tool_calls" in result
    
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    @patch('src.agent.core.AgentExecutor')
    def test_run_with_error(self, mock_executor_class, mock_create_agent, mock_chatgpt, mock_langsmith, mock_tools):
        """Test agent run with error"""
        mock_langsmith.return_value = None
        
        # Setup mock executor to raise exception
        mock_executor = Mock()
        mock_executor.invoke.side_effect = Exception("Test error")
        mock_executor_class.return_value = mock_executor
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        result = agent.run("Test query")
        
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]
    
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    @patch('src.agent.core.AgentExecutor')
    def test_run_with_rate_limit_error(self, mock_executor_class, mock_create_agent, mock_chatgpt, mock_langsmith, mock_tools):
        """Test agent run with rate limit error"""
        mock_langsmith.return_value = None
        
        # Setup mock executor to raise rate limit exception
        mock_executor = Mock()
        mock_executor.invoke.side_effect = Exception("rate limit exceeded")
        mock_executor_class.return_value = mock_executor
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        result = agent.run("Test query")
        
        assert result["success"] is False
        assert "rate limit" in result["output"].lower()
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_tool_call_count_tracking(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test tool call count tracking"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        
        assert agent.get_tool_call_count() == 0
        
        # Simulate tool calls
        agent.tool_limit_callback.on_tool_start({}, "test")
        assert agent.get_tool_call_count() == 1
        
        agent.reset_tool_call_count()
        assert agent.get_tool_call_count() == 0
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_memory_operations(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test memory operations"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, use_memory=True, enable_langsmith=False)
        
        # Test clearing memory
        agent.clear_memory()
        
        # Test getting memory context
        context = agent.get_memory_context()
        assert isinstance(context, list)
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    def test_check_tool_call_limit(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor, mock_tools):
        """Test checking tool call limit"""
        mock_langsmith.return_value = None
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        
        assert agent.check_tool_call_limit() is False
        
        # Simulate reaching limit
        for _ in range(agent.max_tool_calls):
            agent.tool_limit_callback.on_tool_start({}, "test")
        
        assert agent.check_tool_call_limit() is True


@pytest.mark.asyncio
class TestResearchAgentAsync:
    """Test async functionality of ResearchAgent"""
    
    @patch('src.agent.core.AgentExecutor')
    @patch('src.agent.core.setup_langsmith_tracing')
    @patch('src.agent.core.ChatOpenAI')
    @patch('src.agent.core.create_react_agent')
    async def test_arun_success(self, mock_create_agent, mock_chatgpt, mock_langsmith, mock_executor_class, mock_tools):
        """Test successful async agent run"""
        mock_langsmith.return_value = None
        
        # Setup mock executor with async mock
        mock_executor = Mock()
        
        # Create an async mock for ainvoke
        async def mock_ainvoke(*args, **kwargs):
            return {
                "output": "Async test response",
                "intermediate_steps": []
            }
        
        mock_executor.ainvoke = mock_ainvoke
        mock_executor_class.return_value = mock_executor
        
        agent = ResearchAgent(tools=mock_tools, enable_langsmith=False)
        result = await agent.arun("Test query")
        
        assert result["success"] is True
        assert result["output"] == "Async test response"
        assert "tool_calls" in result
