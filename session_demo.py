import asyncio

from agents import Agent, Runner, SQLiteSession

async def main():
    # Create agent
    agent = Agent(
        name="Assistant",
        instructions="Reply very concisely about the mentioned topic.",
    )

    # Create a session instance with a session ID
    session = SQLiteSession("steve_ferns_96","conversations.db")

    # First turn
    result = await Runner.run(
        agent,
        "Which anime is monkey de luffy from ?",
        session=session
    )
    print(result.final_output)  # "San Francisco"

    # Second turn - agent automatically remembers previous context
    result = await Runner.run(
        agent,
        "Who is he in the show?",
        session=session
    )
    print(result.final_output)  # "California"

    # Also works with synchronous runner
    result = await Runner.run(
        agent,
        "What episode is it currently airing?",
        session=session
    )
    print(result.final_output) 
    # "Approximately 39 million"


if __name__ == "__main__":
    asyncio.run(main())