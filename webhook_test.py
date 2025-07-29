from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
  model="4o-mini",
  input="Write a very long novel about otters in space.",
  background=True,
)

print(resp.status)