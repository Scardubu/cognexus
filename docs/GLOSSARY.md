# Glossary

Short definitions for terms used in Cognexus documentation.

| Term | Plain-English Definition |
|---|---|
| API | A way for one program to talk to another program. Cognexus exposes an HTTP API. |
| API key | A secret value used to prove a request is allowed. Keep it private. |
| Dry run | A safe test that does not call OpenAI or spend credits. |
| Execution mode | The working style for a request, such as `focus`, `review`, or `incident`. |
| Guardrail | A safety check that rejects unsafe input or output. |
| Health check | A simple endpoint that confirms the server process is alive. |
| Metrics | Numbers about the system, such as request counts and latency. |
| OpenTelemetry | A standard way to collect traces and operational signals. |
| Prometheus | A common tool for collecting and querying metrics. |
| Readiness check | A deeper check that confirms important dependencies are usable. |
| Redis | A fast shared data store used for production sessions and rate limits. |
| Session | A named conversation history. |
| SQLite | A small local database file used for development sessions. |
| Skill | A reusable instruction pack for a specialized kind of work. |
| Trace | A record of important steps during one request, useful for debugging. |
| Uvicorn | The Python web server that runs the Cognexus FastAPI app. |
| Virtual environment | A local Python folder, usually `.venv`, that keeps project packages separate. |

## Related Reading

- Beginner walkthrough: [../QUICKSTART.md](../QUICKSTART.md)
- User guide: [USER_GUIDE.md](USER_GUIDE.md)
- API guide: [API.md](API.md)
- Troubleshooting: [../TROUBLESHOOTING.md](../TROUBLESHOOTING.md)
