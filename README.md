# Mandala Chart MCP

Generate your Mandala Chart with a provided goal. Files can be used in order to find your main goal.

## Prerequisites

- Python 3.9+
- Groq API key

## Setup

### Step 1: Configure the environment variables

1. Create the `.env` file in the project root and set your values:

```
MODEL="" # Enter the model you will use (openai/gpt-oss-20b is recommended)
GROQ_API_KEY=""  # Enter your API secret key
```

### Step 2: Install dependencies

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

1. Install uv, if not already installed:

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:

```bash
uv sync
```

4. Run the project

```bash
uv run main.py
```

## Usage

### Automatic generation from a goal

Use /generate_mandalart command followed by your main goal to create your Mandala Chart in Markdown format.

### Automatic generation from a file

In case of not having a creal goal, you can also use /generate_mandalart command followed by the path of a document that contain important information in order to generate the main goal and the rest of the chart.
