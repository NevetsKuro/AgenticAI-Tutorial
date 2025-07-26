import asyncio
import sys
from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from agents.exceptions import InputGuardrailTripwireTriggered
from pydantic import BaseModel
from tri_agent import history_tutor_agent, math_tutor_agent

class HomeworkOutput(BaseModel):
    is_history_qtn: bool
    reasoning: str

guardrail_agent = Agent(
    name="Guardrail check",
    instructions="Check if the user is asking about a history question.",
    output_type=HomeworkOutput,
)

# Only allow questions related to history
async def history_guardrail(ctx, agent, input_data):
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)
    return GuardrailFunctionOutput(
        output_info=final_output,
        tripwire_triggered=not final_output.is_history_qtn,
    )

triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's homework question",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=history_guardrail),
    ],
)

if __name__ == "__main__":
    try:
      if len(sys.argv) > 1:
          data = sys.argv[1:] # Get all arguments after the script name
          print(f"Question asked - {data[0]}")
          result = asyncio.run(Runner.run(triage_agent, data[0]))
          print(result)
      else:
          print("No data provided via command-line arguments.")

    except InputGuardrailTripwireTriggered as e:
        print("Guardrail blocked this input:", e)
