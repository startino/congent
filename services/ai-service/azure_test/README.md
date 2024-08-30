# Template for creating a new knowledge graph.

### How to use this template

1. Setup the folder
```bash
# Create a new folder for the project
cp -r kg_project_template new_project_name

# Copy the sample data into the input folder
cp -r ./sample_readai_data ./new_project_name/input
```
2. Init the GraphRAG project.
```bash
python -m graphrag.index --init --root ./new_project_name
```

3. Start Indexing
```bash
python -m graphrag.index --verbose --root ./new_project_name --reporter rich --emit csv --nocache
```
