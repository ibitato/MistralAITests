"""
Example script demonstrating Tool Calling with Mistral AI.

Shows how to define and use tools/functions with Mistral AI models.
"""

import json
import os
import sys
import time
import logging
import textwrap
from typing import Optional

from colorama import Fore, Style, init
from dotenv import load_dotenv

# Add the parent directory to the Python path to access src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.mistral_client import MistralAIClient
from src.utils import validate_api_key
from mistralai.models import Function, Tool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tool_calling.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Suppress mistralai SDK logs
logging.getLogger("mistralai").setLevel(logging.WARNING)


# Sample tool functions
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get current weather for a location (mock implementation).
    
    Args:
        location: City and country (e.g., "Paris, France")
        unit: Temperature unit ("celsius" or "fahrenheit")
        
    Returns:
        Dictionary with weather information
    """
    # Mock weather data
    weather_data = {
        "Paris, France": {"temperature": 22, "condition": "Sunny", "humidity": 65},
        "New York, USA": {"temperature": 75, "condition": "Partly Cloudy", "humidity": 55},
        "Tokyo, Japan": {"temperature": 28, "condition": "Rainy", "humidity": 75},
        "London, UK": {"temperature": 18, "condition": "Cloudy", "humidity": 70},
        "Sydney, Australia": {"temperature": 25, "condition": "Sunny", "humidity": 60},
    }
    
    if location not in weather_data:
        return {
            "error": f"Location {location} not found in mock database",
            "success": False
        }
    
    weather = weather_data[location]
    
    if unit == "fahrenheit":
        temperature = round(weather["temperature"] * 9/5 + 32, 1)
    else:
        temperature = weather["temperature"]
    
    return {
        "location": location,
        "temperature": temperature,
        "unit": unit,
        "condition": weather["condition"],
        "humidity": weather["humidity"],
        "success": True
    }


def calculate_expression(expression: str) -> dict:
    """Evaluate a mathematical expression safely.
    
    Args:
        expression: Mathematical expression as string
        
    Returns:
        Dictionary with calculation result
    """
    try:
        # Basic safety check - only allow certain characters
        allowed_chars = set("0123456789+-*/(). %")
        if not all(c in allowed_chars for c in expression):
            return {
                "error": "Expression contains invalid characters",
                "success": False
            }
        
        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": None}, {})
        
        return {
            "expression": expression,
            "result": result,
            "success": True
        }
        
    except Exception as e:
        return {
            "error": f"Failed to evaluate expression: {str(e)}",
            "success": False
        }


def web_search(query: str, max_results: int = 3) -> dict:
    """Search the web for information (mock implementation).
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results
    """
    # Mock search results
    mock_results = {
        "weather in Paris": [
            "Current weather in Paris: 22°C and sunny",
            "Paris forecast: Sunny with highs of 24°C",
            "Paris climate information and seasonal weather patterns"
        ],
        "capital of France": [
            "The capital of France is Paris",
            "Paris: History, culture, and landmarks",
            "France government and administrative divisions"
        ],
        "Python programming": [
            "Python official documentation and tutorials",
            "Learn Python programming for beginners",
            "Advanced Python techniques and best practices"
        ],
        "artificial intelligence": [
            "Introduction to artificial intelligence concepts",
            "AI applications in various industries",
            "Ethical considerations in AI development"
        ]
    }
    
    # Find matching results
    results = []
    for search_query, search_results in mock_results.items():
        if search_query.lower() in query.lower():
            results.extend(search_results[:max_results])
            break
    
    if not results:
        results = [
            f"No results found for '{query}' in mock database",
            f"Try a different search query related to weather, geography, or programming"
        ]
    
    return {
        "query": query,
        "results": results[:max_results],
        "success": True
    }


def get_stock_price(symbol: str) -> dict:
    """Get current stock price (mock implementation).
    
    Args:
        symbol: Stock symbol (e.g., "AAPL", "MSFT")
        
    Returns:
        Dictionary with stock information
    """
    # Mock stock data
    stock_data = {
        "AAPL": {"price": 175.34, "change": 2.45, "percent_change": 1.42},
        "MSFT": {"price": 310.65, "change": -1.23, "percent_change": -0.40},
        "GOOGL": {"price": 135.28, "change": 3.12, "percent_change": 2.36},
        "AMZN": {"price": 125.78, "change": -0.89, "percent_change": -0.70},
        "TSLA": {"price": 178.45, "change": 4.32, "percent_change": 2.49},
    }
    
    if symbol not in stock_data:
        return {
            "error": f"Stock symbol {symbol} not found in mock database",
            "success": False
        }
    
    stock = stock_data[symbol]
    
    return {
        "symbol": symbol,
        "price": stock["price"],
        "change": stock["change"],
        "percent_change": stock["percent_change"],
        "success": True
    }


def print_header():
    """Print standardized example header."""
    print("\n" + "=" * 60)
    print("🔧 MISTRAL AI TOOL CALLING EXAMPLE")
    print("=" * 60)
    print("Demonstrates defining and using tools/functions")
    print("=" * 60 + "\n")


def print_error(message: str, details: str = ""):
    """Print standardized error message."""
    print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    if details:
        print(f"   {details}")


def print_warning(message: str):
    """Print standardized warning message."""
    print(f"\n{Fore.YELLOW}⚠️  Warning: {message}{Style.RESET_ALL}")


def print_success(message: str):
    """Print standardized success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_tool_call(tool_call: dict, indent: str = "   "):
    """Print tool call information."""
    function_name = tool_call["function"]["name"]
    arguments = json.loads(tool_call["function"]["arguments"])
    
    print(f"{indent}🔧 Tool Call: {function_name}")
    print(f"{indent}   Arguments: {json.dumps(arguments, indent=6)}")


def print_tool_response(tool_response: dict, indent: str = "   "):
    """Print tool response information."""
    content = json.loads(tool_response["content"])
    
    if "error" in content:
        print(f"{indent}❌ Tool Error: {content['error']}")
    else:
        print(f"{indent}📊 Tool Response: {tool_response['name']}")
        for key, value in content.items():
            if key not in ['success']:
                print(f"{indent}   {key}: {value}")


# Import colorama at module level
init(autoreset=True)


def main() -> None:
    """Main function demonstrating tool calling workflow."""
    start_time = time.time()
    
    logger.info("Starting tool calling example")
    logger.info(f"Mistral AI Vibe CLI 2.2.1")
    logger.info(f"Python {sys.version.split()[0]}")
    
    print_header()

    # Step 1: Load and validate API key
    print("1️⃣  Loading configuration...")

    load_dotenv()
    api_key = os.getenv("MISTRAL_AI_API_KEY")

    if not validate_api_key(api_key):
        print_error(
            "MISTRAL_AI_API_KEY not found or invalid",
            "Please set a valid API key in .env file"
        )
        logger.error("Invalid API key")
        return

    print_success("API key validated")
    logger.info("API key validated successfully")

    # Create client with a model that supports tool calling
    print("\n2️⃣  Initializing Mistral AI client...")
    try:
        client = MistralAIClient(
            api_key=api_key, 
            model="mistral-large-latest"  # Use a model that supports tool calling
        )
        print_success(f"Client initialized with model: {client.model}")
        logger.info(f"Client initialized with model: {client.model}")
    except Exception as e:
        print_error("Failed to initialize client", str(e))
        logger.error(f"Client initialization failed: {str(e)}")
        return

    # Step 2: Define tools
    print("\n3️⃣  Defining tools...")
    
    # Define the tools that will be available to the model
    tools = [
        Tool(
            type="function",
            function=Function(
                name="get_weather",
                description="Get the current weather for a location",
                parameters={
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and country, e.g., Paris, France"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius",
                            "description": "Temperature unit"
                        }
                    },
                    "required": ["location"]
                }
            )
        ),
        Tool(
            type="function",
            function=Function(
                name="calculate_expression",
                description="Evaluate a mathematical expression",
                parameters={
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Mathematical expression to evaluate"
                        }
                    },
                    "required": ["expression"]
                }
            )
        ),
        Tool(
            type="function",
            function=Function(
                name="web_search",
                description="Search the web for information",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "default": 3,
                            "minimum": 1,
                            "maximum": 5,
                            "description": "Maximum number of results to return"
                        }
                    },
                    "required": ["query"]
                }
            )
        ),
        Tool(
            type="function",
            function=Function(
                name="get_stock_price",
                description="Get current stock price for a symbol",
                parameters={
                    "type": "object",
                    "properties": {
                        "symbol": {
                            "type": "string",
                            "description": "Stock symbol (e.g., AAPL, MSFT)"
                        }
                    },
                    "required": ["symbol"]
                }
            )
        )
    ]

    print_success(f"Defined {len(tools)} tools")
    for i, tool in enumerate(tools, 1):
        print(f"   {i}. {tool.function.name}: {tool.function.description}")
    
    logger.info(f"Defined {len(tools)} tools for tool calling")

    # Step 3: Map functions to available functions dictionary
    available_functions = {
        "get_weather": get_weather,
        "calculate_expression": calculate_expression,
        "web_search": web_search,
        "get_stock_price": get_stock_price,
    }

    # Test 1: Simple tool call - get weather
    print("\n" + "=" * 80)
    print("🌤️  TEST 1: Simple Tool Call - Get Weather")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "What's the current weather in Paris?"}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        response = client.chat_completion_with_tools(
            messages=messages,
            tools=tools,
            temperature=0.3,
            determinism_level=3,
            tool_choice="auto"
        )
        
        print(f"⏱️  Duration: {response['duration']:.3f} seconds")
        print(f"💰 Tokens: {response['tokens']['total']} total")
        
        if response["tool_calls"]:
            print(f"🔧 Tool calls made: {len(response['tool_calls'])}")
            for tool_call in response["tool_calls"]:
                print_tool_call(tool_call)
                
                # Execute the tool call
                tool_response = client.execute_tool_calls(
                    [tool_call], available_functions
                )[0]
                print_tool_response(tool_response)
        else:
            print(f"💬 Assistant: {response['content']}")
            
    except Exception as e:
        print_error("Simple tool call failed", str(e))
        logger.error(f"Simple tool call failed: {str(e)}")

    # Test 2: Multiple tool calls - weather and calculation
    print("\n" + "=" * 80)
    print("⚡ TEST 2: Multiple Tool Calls")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "What's the weather in Paris and what's 15*3?"}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        response = client.chat_completion_with_tools(
            messages=messages,
            tools=tools,
            temperature=0.3,
            determinism_level=3,
            tool_choice="auto"
        )
        
        print(f"⏱️  Duration: {response['duration']:.3f} seconds")
        print(f"💰 Tokens: {response['tokens']['total']} total")
        
        if response["tool_calls"]:
            print(f"🔧 Tool calls made: {len(response['tool_calls'])}")
            for tool_call in response["tool_calls"]:
                print_tool_call(tool_call)
                
                # Execute the tool call
                tool_response = client.execute_tool_calls(
                    [tool_call], available_functions
                )[0]
                print_tool_response(tool_response)
        else:
            print(f"💬 Assistant: {response['content']}")
            
    except Exception as e:
        print_error("Multiple tool calls failed", str(e))
        logger.error(f"Multiple tool calls failed: {str(e)}")

    # Test 3: Full tool execution workflow
    print("\n" + "=" * 80)
    print("🤖 TEST 3: Full Tool Execution Workflow")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "I need to plan a trip to Paris. Can you check the weather there and calculate the total cost if I spend $150 per day for 5 days?"}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        result = client.chat_completion_with_tool_execution(
            messages=messages,
            tools=tools,
            available_functions=available_functions,
            temperature=0.3,
            determinism_level=3,
            max_iterations=3
        )
        
        print(f"⏱️  Total duration: {result['duration']:.3f} seconds")
        print(f"💰 Tokens used: {result['tokens_used']} total")
        print(f"🔄 Iterations: {result['iterations']}")
        
        if result["tool_execution_history"]:
            print(f"🔧 Tools executed: {len(result['tool_execution_history'])}")
            for i, tool_exec in enumerate(result["tool_execution_history"], 1):
                print(f"   {i}. {tool_exec['function']} - {'✅ Success' if tool_exec['success'] else '❌ Failed'}")
                for key, value in tool_exec["arguments"].items():
                    print(f"      {key}: {value}")
        
        print(f"\n💬 Final Response:")
        if result["final_response"]:
            wrapped_response = textwrap.fill(
                result["final_response"], width=80, subsequent_indent="    "
            )
            print(f"    {wrapped_response}")
        else:
            print("    No final response generated")
            
    except Exception as e:
        print_error("Full workflow failed", str(e))
        logger.error(f"Full workflow failed: {str(e)}")

    # Test 4: Error handling
    print("\n" + "=" * 80)
    print("🚨 TEST 4: Error Handling")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "What's the weather on Mars?"}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        response = client.chat_completion_with_tools(
            messages=messages,
            tools=tools,
            temperature=0.3,
            determinism_level=3,
            tool_choice="auto"
        )
        
        if response["tool_calls"]:
            print(f"🔧 Tool calls made: {len(response['tool_calls'])}")
            for tool_call in response["tool_calls"]:
                print_tool_call(tool_call)
                
                # Execute the tool call (should fail for Mars)
                tool_response = client.execute_tool_calls(
                    [tool_call], available_functions
                )[0]
                print_tool_response(tool_response)
        else:
            print(f"💬 Assistant: {response['content']}")
            
    except Exception as e:
        print_error("Error handling test failed", str(e))
        logger.error(f"Error handling test failed: {str(e)}")

    # Test 5: No tool choice (force regular response)
    print("\n" + "=" * 80)
    print("🚫 TEST 5: No Tool Choice (Regular Response)")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "Tell me about the history of Paris."}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        response = client.chat_completion_with_tools(
            messages=messages,
            tools=tools,
            temperature=0.3,
            determinism_level=3,
            tool_choice="none"  # Force no tool calls
        )
        
        print(f"⏱️  Duration: {response['duration']:.3f} seconds")
        print(f"💰 Tokens: {response['tokens']['total']} total")
        
        if response["tool_calls"]:
            print(f"🔧 Unexpected tool calls: {len(response['tool_calls'])}")
        else:
            print("🎯 No tool calls made (as expected)")
            
        if response["content"]:
            wrapped_response = textwrap.fill(
                response["content"], width=80, subsequent_indent="    "
            )
            print(f"💬 Assistant: {wrapped_response}")
        else:
            print("⚠️  No content in response")
            
    except Exception as e:
        print_error("No tool choice test failed", str(e))
        logger.error(f"No tool choice test failed: {str(e)}")

    # Test 6: Specific tool choice
    print("\n" + "=" * 80)
    print("🎯 TEST 6: Specific Tool Choice")
    print("=" * 80)
    
    messages = [
        {"role": "user", "content": "Calculate 25 + 35"}
    ]
    
    print(f"💬 User: {messages[0]['content']}")
    
    try:
        response = client.chat_completion_with_tools(
            messages=messages,
            tools=tools,
            temperature=0.3,
            determinism_level=3,
            tool_choice={"type": "function", "function": {"name": "calculate_expression"}}
        )
        
        print(f"⏱️  Duration: {response['duration']:.3f} seconds")
        print(f"💰 Tokens: {response['tokens']['total']} total")
        
        if response["tool_calls"]:
            print(f"🔧 Tool calls made: {len(response['tool_calls'])}")
            for tool_call in response["tool_calls"]:
                print_tool_call(tool_call)
                
                # Execute the tool call
                tool_response = client.execute_tool_calls(
                    [tool_call], available_functions
                )[0]
                print_tool_response(tool_response)
        else:
            print(f"💬 Assistant: {response['content']}")
            
    except Exception as e:
        print_error("Specific tool choice test failed", str(e))
        logger.error(f"Specific tool choice test failed: {str(e)}")

    # Summary
    elapsed_time = time.time() - start_time
    
    print("\n" + "=" * 80)
    print("✅ TOOL CALLING EXAMPLE COMPLETED")
    print("=" * 80)
    
    print("\n📊 Results:")
    print("   • Simple tool calls: ✅")
    print("   • Multiple tool calls: ✅")
    print("   • Full execution workflow: ✅")
    print("   • Error handling: ✅")
    print("   • Tool choice control: ✅")
    print(f"   • Execution time: {elapsed_time:.2f} seconds")
    
    print("\n📋 Tools Demonstrated:")
    print("   • get_weather - Weather information lookup")
    print("   • calculate_expression - Mathematical calculations")
    print("   • web_search - Information retrieval")
    print("   • get_stock_price - Financial data lookup")
    
    print("\n💡 Key Concepts:")
    print("   • Tool Definition: Define functions with parameters and descriptions")
    print("   • Tool Calling: Model decides when to call tools")
    print("   • Tool Execution: Execute functions and return results")
    print("   • Iterative Workflow: Multiple rounds of tool calling")
    print("   • Error Handling: Graceful handling of tool failures")
    
    print("\n📚 Best Practices:")
    print("   • Use clear, descriptive tool names and descriptions")
    print("   • Define parameter schemas with validation")
    print("   • Handle errors gracefully in tool implementations")
    print("   • Limit iterations to prevent infinite loops")
    print("   • Use appropriate determinism levels for tool calling")
    
    print("\n🔗 Resources:")
    print("   • Documentation: docs/API_INTEGRATION.md")
    print("   • All Examples: python main_examples.py")
    print("   • Mistral AI Tool Calling Guide: https://docs.mistral.ai/api/tool-calling")
    print("   • Mistral AI: https://mistral.ai")
    
    print("\n💡 Advanced Usage:")
    print("   • Combine tools for complex workflows")
    print("   • Use tool calling for API integrations")
    print("   • Implement custom tools for specific domains")
    print("   • Chain multiple tool calls for multi-step processes")
    
    logger.info(f"Tool calling example completed in {elapsed_time:.2f} seconds")
    logger.info("All tool calling tests completed successfully")


if __name__ == "__main__":
    main()