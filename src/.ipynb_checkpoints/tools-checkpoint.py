import polars as pl
from langchain.tools import tool
from psycopg_pool import ConnectionPool

def make_tools(pool):
    
    def get_pokemon_id(name: str) -> dict:
        """Get the PokeAPI database id for the Pokemon with the given name. Name should be provided in lowercase, with spaces replaced by a dash `-`.
        Args:
            name (str): Pokemon's name, in lowercase, with spaces replaced by a dash `-`.
        """
        name = name.lower()
        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name
                    FROM pokemon_v2_pokemon
                    WHERE name = %(name)s
                    """,
                    {
                        "name": name
                    }
                )
                
                row = cur.fetchone()

        if row is None:
            return {"name": name, "error_msg": "Could not find this name in the database"}

        return {
            "id": row[0],
            "name": row[1]
        }
    
    @tool
    def get_pokemon_types(name: str) -> dict:
        """Get the type or types of the given Pokemon.
        Args:
            name (str): Pokemon's name, in lowercase, with spaces replaced by a dash `-`.
        """
        pokeid = get_pokemon_id(name)
        if "id" not in pokeid:
            return pokeid

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select pvt.name, pvp.slot 
                    from pokemon_v2_pokemontype pvp
                    join pokemon_v2_type pvt 
                    on pvp.type_id = pvt.id 
                    where pokemon_id = %(pokeid)s
                    """,
                    {
                        "pokeid": pokeid["id"]
                    }
                )
                
                rows = cur.fetchall()

        if rows == []:
            return {"name": name, "error_msg": f"Could not find types for {name} in the database"}
    
        types = {
            f"type_{row[1]}": row[0] for row in rows
        }
        types["name"] = name
        
        return types
    
    @tool
    def get_pokemon_moves_by_level(name: str):
        """Get the movements that a Pokemon learns by leveling up. Information corresponds to latest game version group
        where the Pokemon appears. Pokemon Champions is excluded, as Pokemon do not level there.
        Args:
            name (str): Pokemon's name, in lowercase, with spaces replaced by a dash `-`.
        """
        pokeid = get_pokemon_id(name)
        if "id" not in pokeid:
            return pokeid

        with pool.connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select
                        pm.level,
                        pm.order,
                        -- pm.move_learn_method_id,
                        -- mlm.name method_name,
                        m.name move_name,
                        t.name type_name,
                        pm.version_group_id,
                        vg.name version_name
                    from pokemon_v2_pokemonmove pm
                    join pokemon_v2_move m 
                        on pm.move_id = m.id
                    join pokemon_v2_movelearnmethod mlm
                        on pm.move_learn_method_id = mlm.id
                    join pokemon_v2_type t
                        on m.type_id = t.id
                    join pokemon_v2_versiongroup vg
                        on pm.version_group_id = vg.id
                    where 
                        pm.pokemon_id = %(pokeid)s
                        and mlm.name = 'level-up'
                        and vg."order" = (
                            select max(vg2."order")
                            from pokemon_v2_pokemonmove pm2
                            join pokemon_v2_versiongroup vg2
                                on pm2.version_group_id = vg2.id
                            where pm2.pokemon_id = pm.pokemon_id and pm2.version_group_id != 32 -- exclude Pokemon Champions, there is no leveling
                        )
                    """,
                    {
                        "pokeid": pokeid["id"]
                    }
                )
                rows = cur.fetchall()
                columns = [desc.name for desc in cur.description]


        if rows == []:
            return {"name": name, "error_msg": f"Could not find moves for {name} in the database"}

        version_group = rows[0][-1]
        df = pl.DataFrame(rows, schema=columns, orient="row").drop("version_group_id", "version_name")
        return {
            "name": name,
            "moves": df.to_dicts(),
            "version_group": version_group,
        }

    return [get_pokemon_types, get_pokemon_moves_by_level]