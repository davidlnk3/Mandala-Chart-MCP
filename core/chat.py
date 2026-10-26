import groq
from mcp_client import MCPClient
from core.tools import ToolManager
from anthropic.types import MessageParam


class Chat:
    def __init__(self, claude_service: groq.Groq, clients: dict[str, MCPClient]):
        self.service: groq.Groq = claude_service
        self.clients: dict[str, MCPClient] = clients
        self.messages: list[MessageParam] = []

    async def _process_query(self, query: str):
        self.messages.append({"role": "user", "content": query})

    async def run(
        self,
        query: str,
    ) -> str:
        final_text_response = ""

        await self._process_query(query)

        while True:
            response = self.service.chat(
                messages=self.messages,
                tools=await ToolManager.get_all_tools(self.clients),
            )

            self.service.add_assistant_message(
                self.messages, response.choices[0].message
            )

            choice = response.choices[0]
            if choice.finish_reason == "tool_calls":
                print(self.service.text_from_message(response))
                tool_result_messages = await ToolManager.execute_tool_requests(
                    self.clients, choice.message
                )

                self.messages.extend(tool_result_messages)
            else:
                final_text_response = self.service.text_from_message(
                    response
                )
                break

        return final_text_response
