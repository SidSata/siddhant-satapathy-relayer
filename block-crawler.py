import sys
import sqlite3
from web3 import Web3

class BlockCrawler:
    """
    Crawls Ethereum blocks and stores transactions in a SQLite database. 

    Parameters: 
    rpc_endpoint (str): The RPC endpoint of the Ethereum client to connect to.
    db_path (str): The path to the SQLite database file to store the transactions in.
    start_block (int): The block number to start crawling from.
    end_block (int): The block number to end crawling at.

    Methods:
    initialize_endpoints(): Initializes the connection to the Ethereum client.
    initialize_database(): Initializes the connection to the SQLite database.
    initialize(): Calls initialize_endpoints() and initialize_database().
    create_tables(): Creates the tables in the SQLite database.
    populate_block(block_number): Populates the database with transactions from the given block.
    populate_range(start_block, end_block): Populates the database with transactions from the given range of blocks.
    run(): Runs the crawler and populates the database range. Calls initialize() and populate_range().
    """

    def __init__(self, rpc_endpoint, db_path, start_block, end_block):
        self.rpc_endpoint = rpc_endpoint
        self.db_path = db_path
        self.start_block = start_block
        self.end_block = end_block
        self.w3 = None
        self.conn = None

    def initialize_endpoints(self) -> None:
        """
        Initializes the connection to the Ethereum client. Fails if self.rpc_endpoint is None or invalid.
        """
        self.w3 = Web3(Web3.HTTPProvider(self.rpc_endpoint))
        if not self.w3.is_connected():
            print("Failed to connect to Ethereum client. Please retry using a different RPC endpoint.")
            sys.exit(1)
        else:
            print("Connected to Ethereum client.")

    def initialize_database(self) -> None:
        """
        Initializes the connection to the SQLite database. Fails if self.db_path is None or invalid.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print("Failed to connect to database.")
            sys.exit(1)

    def initialize(self) -> None:
        """
        Initializes the crawler. Calls initialize_endpoints() and initialize_database().
        """
        self.initialize_endpoints()
        self.initialize_database()
    
    def create_tables(self) -> bool:
        """
        Creates the blocks and transactions tables in the SQLite database. 
        """
        if not self.cursor:
            print("Database connection not initialized.")
            sys.exit(1)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS blocks (
            hash TEXT PRIMARY KEY,
            number TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            total_volume REAL DEFAULT 0
        )
        ''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
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
        ''')

    def populate_block(self, block_number) -> None:
        """
        Retrieves the Ethereum block from the RPC and populates the blocks database with retrieved block
        and the transactions table with the transactions from the given block.
        """
        print("Populating block", block_number)
        block = self.w3.eth.get_block(block_number, full_transactions=True)
        total_volume = 0
        for tx in block.transactions:
            current_volume = float(self.w3.from_wei(tx.value, 'ether'))
            self.cursor.execute('''
            INSERT OR IGNORE  INTO transactions (
                tx_hash,
                block_hash,
                from_address,
                to_address,
                value,
                gas,
                gas_price,
                nonce
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                tx.hash.hex(),
                tx.blockHash.hex(),
                tx['from'],
                tx.to if tx.to else '', 
                current_volume,
                tx.gas,
                tx.gasPrice,
                tx.nonce
            ))
            total_volume += current_volume
        self.cursor.execute('''
        INSERT OR IGNORE INTO blocks (
            hash,
            number,
            timestamp,
            total_volume
        ) VALUES (?, ?, ?, ?)
        ''', (
            block.hash.hex(),
            block.number,
            block.timestamp,
            total_volume,
        ))
        print("Successfully populated block", block_number)

    def populate_range(self, start_block, end_block) -> None:
        """
        Calls populate_block for a range of blocks and populates the SQLite database with the transactions from the given range of blocks.
        """
        for block_number in range(start_block, end_block + 1):
            self.populate_block(block_number)

        
    
    def run(self):
        """
        Runs the crawler and populates the database range. Calls initialize() and populate_range().
        """
        self.initialize()
        self.create_tables()
        self.populate_range(self.start_block, self.end_block)
        print(f"Transactions from blocks {self.start_block} to {self.end_block} have been stored in {self.db_path}")
        
        # Closes database connection
        self.conn.commit()
        self.conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python block-crawler.py <RPC_ENDPOINT> <DB_PATH> <BLOCK_RANGE>")
        sys.exit(1)
    rpc_endpoint = sys.argv[1]
    db_path = sys.argv[2]
    block_range = sys.argv[3]
    try:
        start_block, end_block = map(int, block_range.split('-'))
    except ValueError:
        print("Block range must be in the format 'start-end'.")
        sys.exit(1)
    # Initialize the crawler
    crawler = BlockCrawler(rpc_endpoint, db_path, start_block, end_block)
    # Run the crawler
    crawler.run()



    