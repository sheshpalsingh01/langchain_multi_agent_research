# Multi-Agent Research Assistant

A LangChain research assistant that searches the web, reads a source article, writes a report, and reviews the result. Run it from the command line or use the local Flask web interface.

## How it works

```text
Research topic → Search agent → Reader agent → Writer chain → Critic chain
                    │               │               │              │
               Tavily search   Article scraping    Report       Feedback
```

1. **Search agent:** Uses Tavily to find relevant information, including titles, URLs, and snippets.
2. **Reader agent:** Selects a relevant URL and calls the scraper once. The scraper tries Trafilatura, Readability, and Beautiful Soup to extract readable text.
3. **Writer chain:** Combines search findings and extracted content into an introduction, key findings, conclusion, and sources.
4. **Critic chain:** Reviews the report and returns a score, strengths, areas to improve, and a verdict.

The agents and chains use OpenAI's `gpt-4o-mini`, configured in `src/agents/agents.py`.

## Setup

Use a Python environment compatible with the installed dependencies. Python 3.11+ is a suitable starting point. You will need OpenAI and Tavily API keys and an internet connection.

From this repository's root:

```bash
cd 04_multi_agent_langchain
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead.

Create a `.env` file inside `04_multi_agent_langchain`:

```dotenv
OPENAI_API_KEY=your_openai_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Keep this file private and exclude it from version control. Research requests use external APIs and may incur charges.

The code uses `langchain.agents.create_agent`, which requires LangChain 1.x or later. If you reuse an older environment, upgrade its dependencies:

```bash
python -m pip install --upgrade -r requirements.txt
```

## Run the web UI

From the project folder:

```bash
python app.py
```

Open **http://127.0.0.1:5000**, enter a topic, and select **Start research**. Topics can contain up to 500 characters. The page displays the report, critic feedback, search findings, and source reading after the pipeline finishes.

The UI can open before API keys are configured, but running research requires both keys. Restart the app after changing `.env`.

## Run from the command line

Edit the `topic` variable in `main.py`, then run:

```bash
python main.py
```

The pipeline prints each stage and its output to the terminal.

You can also call it from Python while working in the project folder:

```python
from src.pipelines.agents_pipeline import research_pipeline

result = research_pipeline(topic="How is AI changing education?")
print(result["report"])
print(result["feedback"])
```

The returned dictionary contains `search_results`, `scraped_content`, `report`, and `feedback`.

## Project structure

```text
04_multi_agent_langchain/
├── app.py                         # Flask routes and local server
├── main.py                        # Command-line entry point
├── requirements.txt               # Python dependencies
├── templates/
│   └── index.html                 # Web interface
├── src/
│   ├── agents/
│   │   └── agents.py              # Agent builders, prompts, and chains
│   ├── pipelines/
│   │   └── agents_pipeline.py     # Sequential research workflow
│   └── tools/
│       └── tools.py               # Tavily search and article extraction
├── exprements/
│   └── exprement.ipynb            # Experiment notebook
└── demo.excalidraw                # Diagram file
```

## Local HTTP endpoint

`POST /research` accepts a JSON object with a `topic` field:

```bash
curl -X POST http://127.0.0.1:5000/research \
  -H "Content-Type: application/json" \
  -d '{"topic": "How is AI changing education?"}'
```

A successful response includes `topic` and the four pipeline output fields. Invalid topics return HTTP `400`, missing API keys return `503`, and pipeline failures return `500`. Check the server terminal for failure details.

## Troubleshooting

| Problem | What to check |
| --- | --- |
| Missing API key message | Set both keys in the project `.env` file and restart the app. |
| `ModuleNotFoundError` or missing `create_agent` | Activate the intended environment and install or upgrade the requirements there. |
| Reader seems slow | Watch the terminal for source selection, fetching, extraction, and completion messages. Some websites block automated access or respond slowly. |
| Model request times out | Check connectivity and API availability. Model requests have a 45-second timeout and automatic retries are disabled. |
| Reader hits its step limit | The reader is capped at six graph steps. Inspect the source URLs and tool output in the terminal before retrying. |
| Source cannot be read | Try a different topic or source. Paywalls, JavaScript-only pages, and blocked requests can prevent extraction. |
| Port 5000 is occupied | Stop the process using it or change the port in `app.py`. |

## Limitations

- Research runs sequentially; the web page receives results when the entire pipeline completes.
- The reader extracts up to 5,000 characters from one selected source. It returns the tool result directly, including scraping error messages, to avoid repeated scraping loops.
- Scraping uses a 5-second connection timeout and a 15-second read timeout. These are network operation limits, not a deadline for the whole research workflow.
- Reports and critic scores are AI-generated. Verify important claims and citations against the original sources.
- The Flask entry point is intended for local development. It does not include authentication, background jobs, or persistent report storage.
