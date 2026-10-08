# Self hosting PokeAPI

The `docker-compose.yml` creates a local instance of the PokeAPI API and Postgres database. A `.env` file is expected with a random
string that will serve as the password for the database.

To download the data that will populate the database, execute the following commands:

```bash
mkdir -p bootstrap data/postgres

curl -L \
  -o bootstrap/pokeapi.pgdump \
  https://github.com/PokeAPI/pokeapi/releases/download/master-branch/pokeapi.pgdump
```
