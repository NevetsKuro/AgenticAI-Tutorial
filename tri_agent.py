# from agents import Agent, Runner

# agent = Agent(name="Assistant", instructions="You are a helpful assistant")

# result = Runner.run_sync(agent, "Write a haiku about recursion in programming.")
# print(result.final_output)

# Code within the code,
# Functions calling themselves,
# Infinite loop's dance.

import asyncio
from agents import Agent, Runner

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent]
)

async def tri_agent_main():
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(tri_agent_main())