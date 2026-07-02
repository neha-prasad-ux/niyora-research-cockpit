"""One-time: push the local research.db up to MotherDuck.
Run:  MOTHERDUCK_TOKEN=xxxx python3 migrate_to_motherduck.py
"""
import os, duckdb
token = os.environ["MOTHERDUCK_TOKEN"]
con = duckdb.connect(f"md:?motherduck_token={token}")
con.execute("CREATE DATABASE IF NOT EXISTS niyora_research")
con.execute("ATTACH 'research.db' AS localdb")
con.execute("CREATE OR REPLACE TABLE niyora_research.papers AS SELECT * FROM localdb.papers")
n = con.execute("SELECT count(*) FROM niyora_research.papers").fetchone()[0]
print(f"uploaded {n} papers to MotherDuck db 'niyora_research'")
con.close()
