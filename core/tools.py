import json
from typing import Optional, List
from mcp.types import CallToolResult, TextContent
from mcp_client import MCPClient
from groq.types.chat import ChatCompletionMessage, ChatCompletionToolMessageParam


class ToolManager:
    @classmethod
    async def get_all_tools(cls, clients: dict[str, MCPClient]) -> list[dict]:
        """Gets all tools from the provided clients in Groq's function format."""
        tools = []
        for client in clients.values():
            tool_models = await client.list_tools()
            tools += [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description,
                        "parameters": t.input_schema,
                    },
                }
                for t in tool_models
            ]
        return tools

    @classmethod
    async def _find_client_with_tool(
        cls, clients: list[MCPClient], tool_name: str
    ) -> Optional[MCPClient]:
        """Finds the first client that has the specified tool."""
        for client in clients:
            tools = await client.list_tools()
            tool = next((t for t in tools if t.name == tool_name), None)
            if tool:
                return client
        return None

    @classmethod
    def _build_tool_result_part(
        cls, tool_call_id: str, text: str
    ) -> ChatCompletionToolMessageParam:
        """Builds a tool result message for Groq."""
        return {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": text,
        }

    @classmethod
    async def execute_tool_requests(
        cls, clients: dict[str, MCPClient], message: ChatCompletionMessage
    ) -> List[ChatCompletionToolMessageParam]:
        """Executes a list of tool calls against the provided clients."""
        tool_calls = message.tool_calls or []
        tool_result_messages: list[ChatCompletionToolMessageParam] = []
        for tool_call in tool_calls:
            tool_use_id = tool_call.id
            tool_name = tool_call.function.name
            tool_input = json.loads(tool_call.function.arguments or "{}")

            client = await cls._find_client_with_tool(
                list(clients.values()), tool_name
            )

            if not client:
                tool_result_messages.append(
                    cls._build_tool_result_part(
                        tool_use_id, "Could not find that tool"
                    )
                )
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    tool_name, tool_input
                )
                items = []
                if tool_output:
                    items = tool_output.content
                content_list = [
                    item.text for item in items if isinstance(item, TextContent)
                ]
                content = json.dumps(content_list)
            except Exception as e:
                error_message = f"Error executing tool '{tool_name}': {e}"
                print(error_message)
                content = json.dumps({"error": error_message})

            tool_result_messages.append(
                cls._build_tool_result_part(tool_use_id, content)
            )
        return tool_result_messages
