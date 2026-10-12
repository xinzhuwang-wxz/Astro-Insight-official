# Copilot Streaming Contract

Frontend receives Server Sent Events.

Example:

data:
{
  "event":"on_chain_start",
  "name":"planner",
  "data":{}
}

Frontend maps:
planner -> Planning
retriever -> Retrieving data
coder -> Generating code
explainer -> Explaining result