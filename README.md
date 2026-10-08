# Pokemon RAG

The goal of this project is to create an Agentic RAG system that can answer questions about Pokemon.

I am working on this project as a way to put into practice several elements about AI Agents and RAG that I am learning about.

## Work so far
- Simple LangGraph agent with two tools:
  - `get_pokemon_moves_by_level`: returns the moves that a given Pokemon learns while leveling up.
  - `get_pokemon_types`: returns the type or types of a given Pokemon.

## What you need to run it
- HuggingFace API Token, to call on LLMs. Currently only [Qwen3-4B-Instruct-2507](ihttps://huggingface.co/Qwen/Qwen3-4B-Instruct-2507)
is being used.
- [PokeAPI](https://pokeapi.co/) Postgres database. In the `docker/` folder, there are files and instructions to self host
an instance of the PokeAPI API and Postgres database. We only use the database, for now.
