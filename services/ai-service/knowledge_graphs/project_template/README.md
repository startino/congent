# Template for creating a new knowledge graph.

```bash
cd congent/services/ai-service/knowledge_graphs
```

### How to use this template

1. Init
```bash
# Create a new folder for the project
cp -r project_template readai_aug_8

# Init the GraphRAG project.
# "settings-with-secrets.yml" is a file that contains the secrets for the project
# because .env file was not working lol
python -m graphrag.index --init --root ./readai_aug_8 --config settings-with-secrets.yml
```


2. Setup the files
```bash
# Copy the sample data into the input folder
cp -r ../readai_transcripts_from_aug_8 ./readai_aug_8/input

# Copy the .env file
cp project_template/.env readai_aug_8/.env
```


3. Start Indexing
```bash
python -m graphrag.index --root ./readai_aug_8 --reporter rich --config settings-with-secrets.yml
```

##### INDEXING FINISHED #####

Time to view in Neo4j

4. Convert to CSV
```bash
python 