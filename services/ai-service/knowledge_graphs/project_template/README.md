# Template for creating a new knowledge graph.

```bash
cd congent/services/ai-service/knowledge_graphs
```

### How to use this template

1. Init
```bash
# Create a new folder for the project
cp -r project_template project-name-test

# Init the GraphRAG project.
python -m graphrag.index --init --root ./project-name-test
```


2. Setup the files
```bash
# Copy the sample data into the input folder
cp -r ../sample_readai_data ./project-name-test/input

# Copy the .env file
cp project_template/.env project-name-test/.env
```


3. Start Indexing
```bash
python -m graphrag.index --root ./project-name-test --reporter rich
```

##### INDEXING FINISHED #####

4. Convert to CSV
```bash
python 