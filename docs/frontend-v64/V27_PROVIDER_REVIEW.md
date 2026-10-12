# v27 Provider Review

layout.tsx status: found

Decision:
- Did not blindly replace CopilotKit providers.
- Existing provider ordering is preserved.
- Runtime replacement requires checking installed CopilotKit version and provider API.

Next:
- Inspect package.json dependencies
- Confirm CopilotKit runtime contract
- Apply minimal provider change