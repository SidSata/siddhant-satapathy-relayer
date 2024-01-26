# Relayer Technical Challenge

## Usage

1. Install dependencies

```pip install -r requirements.txt```

2. To crawl Ethereum blocks and populate the MySQL database with block and transaction records.

```python block-crawler.py <RPC_ENDPOINT> <DB_PATH> <START_BLOCK-END_BLOCK>```

e.g.

``` python block-crawler.py https://rpc.quicknode.pro/key ./db.sqlite3 18908800-18909050 ```

3. To run a query to get the largest transaction volume block between two timestamps.

```python get-largest-block <DB_PATH> <START_DATE> <END_DATE>```

e.g. 

```python get-largest-block.py db.sqlite3 '2024-01-01 00:00:00' '2024-01-01 00:30:00'```

4. To see the example query for largest transaction volume block between '2024-01-01 00:00:00' and '2024-01-01 00:30:00'

```python get-largest-example.py```


## Notes

1. SQlite DB is prepopulated with blocks and transactions from '2024-01-01 00:00:00' to '2024-01-01 00:30:00'.

2. If RPC endpoint or SQlite DB path is invalid, the block-crawler exits gracefully.

3. result.txt contains the result of Part (2) - highest volume block from '2024-01-01 00:00:00' to '2024-01-01 00:30:00'.

4. To reduce computational overhead assuming a read query heavy system, block volume totals are calculated during retrieval and are stored in the total_volume field.

5. Table schemas

        blocks (
            hash TEXT PRIMARY KEY,
            number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_volume REAL DEFAULT 0
        )
        

        transactions (
            tx_hash TEXT PRIMARY KEY,
            block_hash TEXT NOT NULL,
            from_address TEXT,
            to_address TEXT,
            value REAL,
            gas INTEGER,
            gas_price INTEGER,
            nonce INTEGER,
            FOREIGN KEY (block_hash) REFERENCES blocks (hash)
        )





