


## Python Setup

We're using Poetry for dependency management.

Activate your virtual environment however you like.
I can include the commands for the different methods and OSs later.
Poetry respects any project specific venv you have activated.
So activate it before running any poetry commands.

## Commands for GraphRAG from the Quick Start Guide

### Initializing a project

```bash
python -m graphrag.index --init --root ./<project>
```

### Indexing a project using CLI

```bash
python -m graphrag.index --root ./<project>
```

### Querying a project using CLI (global & local)

```bash
python -m graphrag.query \
--root ./<project> \
--method global \
"What are the top themes in this story?"

python -m graphrag.query \
--root ./<project> \
--method local \
"Who is Scrooge, and what are his main relationships?"
```

## Neo4j

- Make sure docker is running.
- Place the 7 CSV files with "final" into the `neo4j_db/import` folder.
- Username is `neo4j`, password is `hot-potatoes-124`.

Run the follwing command from the root of the project: "congent"
```bash
docker compose up
```

