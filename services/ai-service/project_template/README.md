# Template for creating a new knowledge graph.

```bash
cd congent/services/ai-service/local_kg_projects
```

### How to use this template

1. Init
```bash
# Create a new folder for the project
cp -r ../project_template dhh

# Init the GraphRAG project.
# "settings-with-secrets.yml" is a file that contains the secrets for the project
# because .env file was not working lol
python -m graphrag.index --init --root ./dhh --config settings-with-secrets.yml
```


2. Setup the files
```bash
# Copy the sample data into the input folder
cp -r ../readai_transcripts_from_aug_8 ./dhh/input

# Copy the .env file
cp ../project_template/.env dhh/.env
```


3. Start Indexing
```bash
python -m graphrag.index --root ./dhh --reporter rich --config settings-with-secrets.yml
```

##### INDEXING FINISHED #####

Time to view in Neo4j

4. Convert to CSV
```bash
python 