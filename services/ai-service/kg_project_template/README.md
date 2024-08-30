# Template for creating a new knowledge graph.

```bash
cd congent/services/ai-service
```

### How to use this template

1. Setup the folder
```bash
# Create a new folder for the project
cp -r kg_project_template azure_test

# Copy the sample data into the input folder
cp -r ./sample_readai_data ./azure_test/input
```

2. Init the GraphRAG project.
```bash
python -m graphrag.index --init --root ./azure_test
```


3. Start Indexing
```bash
python -m graphrag.index --verbose --root ./azure_test --reporter rich --nocache
```

##### INDEXING FINISHED #####

4. Convert to CSV
```bash
python 