import groq
from groq.types.chat import ChatCompletion, ChatCompletionMessage


class Groq:
    def __init__(self, model: str, api_key: str):
        self.api_key = api_key
        self.model = model
        self.client = groq.Groq(api_key=api_key)

    def add_user_message(self, messages: list, message):
        user_message = {
            "role": "user",
            "content": message.content
            if isinstance(message, ChatCompletionMessage)
            else message,
        }
        messages.append(user_message)

    def add_assistant_message(self, messages: list, message):
        assistant_message = {
            "role": "assistant",
            "content": message.content
            if isinstance(message, ChatCompletionMessage)
            else message,
        }
        if isinstance(message, ChatCompletionMessage) and message.tool_calls:
            assistant_message["tool_calls"] = [
                tool_call.model_dump() for tool_call in message.tool_calls
            ]
        messages.append(assistant_message)

    def text_from_message(self, response: ChatCompletion):
        return response.choices[0].message.content or ""

    def chat(
        self,
        messages,
        system=None,
        temperature=1.0,
        stop=[],
        tools=None,
        thinking=False,
        thinking_budget=1024,
    ) -> ChatCompletionMessage:
        params = {
            "model": self.model,
            "max_tokens": 4096,
            "messages": messages,
            "temperature": temperature,
            "stop": stop,
        }

        if thinking:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": thinking_budget,
            }

        if tools:
            params["tools"] = tools

        if system:
            params["system"] = system

        message = self.client.chat.completions.create(**params)
        return message
