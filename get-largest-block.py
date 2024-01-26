import sys
import sqlite3

class BlockVolumeQuery:
    def __init__(self, db_path):
        self.db_path = db_path

    def get_largest_volume_block(self, start_date, end_date):
        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # SQL query to find the block with the largest volume of ether transferred
        query = """
        SELECT
            blocks.number,
            total_volume
        FROM
            blocks
        WHERE
            blocks.timestamp BETWEEN strftime('%s', ?) AND strftime('%s', ?)
        ORDER BY
            total_volume DESC
        LIMIT 1;
        """

        # Execute the SQL query with the provided start and end dates
        cursor.execute(query, (start_date, end_date))

        # Fetch the result
        result = cursor.fetchone()

        # Close the database connection
        conn.close()

        # Return the result
        return result

if __name__ == "__main__":
    """
    Usage: python get-largest-block <DB_PATH> <START_DATE> <END_DATE>
    """
    
    if len(sys.argv) != 4:
        print("Usage: python get-largest-block <DB_PATH> <START_DATE> <END_DATE>")
        sys.exit(1)
    
    
    db_path = sys.argv[1]
    start_date = sys.argv[2]
    end_date = sys.argv[3]

    query_tool = BlockVolumeQuery(db_path)

    # Execute the query
    largest_volume_block = query_tool.get_largest_volume_block(start_date, end_date)

    # Print the result
    if largest_volume_block:
        print(f"Block Number: {largest_volume_block[0]}, Total Volume: {largest_volume_block[1]}")
    else:
        print("No blocks found in the specified time range.")