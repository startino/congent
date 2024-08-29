


## Commands for GraphRAG from the Quick Start Guide

```bash
python -m graphrag.index --init --root ./<project>

python -m graphrag.index --root ./<project>

python -m graphrag.query \
--root ./<project> \
--method global \
"What are the top themes in this story?"

python -m graphrag.query \
--root ./<project> \
--method local \
"Who is Scrooge, and what are his main relationships?"
```