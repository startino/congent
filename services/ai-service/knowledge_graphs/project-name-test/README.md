# Template for creating a new knowledge graph.

```bash
cd congent/services/ai-service/knowledge_graphs
```

### How to use this template

1. Setup the folder
```bash
# Create a new folder for the project
cp -r project_template project-name-test

# Copy the sample data into the input folder
cp -r ../sample_readai_data ./project-name-test/input
```

2. Init the GraphRAG project.
```bash
python -m graphrag.index --init --root ./project-name-test
```


3. Start Indexing
```bash
python -m graphrag.index --verbose --root ./project-name-test --reporter rich --nocache
```

##### INDEXING FINISHED #####

4. Convert to CSV
```bash
python 