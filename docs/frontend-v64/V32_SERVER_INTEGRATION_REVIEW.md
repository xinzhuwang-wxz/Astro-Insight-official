# v32 Server Integration Review

Reviewed integration targets:

- Copilot output store
- Backend stream endpoint
- Frontend runtime bridge

Current decision:
Do not replace server Copilot output handling blindly.
The existing project may already contain custom message persistence.

Required next verification:
- inspect copilot-output-store implementation
- inspect route handlers
- unify response format