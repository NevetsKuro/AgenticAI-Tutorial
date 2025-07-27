import asyncio
import random
from typing import Literal

from agents import Agent, RunContextWrapper, Runner


class CustomContext:
    def __init__(self, style: Literal["goku", "luffy", "naruto"]):
        self.style = style


def custom_instructions(
    run_context: RunContextWrapper[CustomContext], agent: Agent[CustomContext]
) -> str:
    context = run_context.context
    if context.style == "goku":
        return "Only respond as the anime character goku from anime tv show Dragon Ball Z."
    elif context.style == "luffy":
        return "Only respond as the anime character luffy from anime tv show One Piece."
    else:
        return "Only respond as the anime character naruto from anime tv show Naruto."

agent = Agent(
    name="Chat agent",
    instructions=custom_instructions,
)


async def main():
    choiceSelected = input("Hi! Select one of the given ? \m ['goku'', 'luffy', 'naruto'] ")
    # choice: Literal["goku", "luffy", "naruto"] = random.choice(["goku", "luffy", "naruto"])
    choice: Literal["goku", "luffy", "naruto"] = choiceSelected
    context = CustomContext(style=choice)
    print(f"Using anime talk style: {choice}\n")

    user_message = "Tell whats your name and what do you do in your daily life. Also tell how fight a bad person in your own way."
    print(f"User: {user_message}")
    result = await Runner.run(agent, user_message, context=context)

    print(f"Assistant: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())

"""
$ python examples/basic/dynamic_system_prompt.py

Using style: haiku

User: Tell me a joke.
Assistant: Why don't eggs tell jokes?
They might crack each other's shells,
leaving yolk on face.

$ python examples/basic/dynamic_system_prompt.py
Using style: robot

User: Tell me a joke.
Assistant: Beep boop! Why was the robot so bad at soccer? Beep boop... because it kept kicking up a debug! Beep boop!

$ python examples/basic/dynamic_system_prompt.py
Using style: pirate

User: Tell me a joke.
Assistant: Why did the pirate go to school?

To improve his arrr-ticulation! Har har har! 🏴‍☠️
"""