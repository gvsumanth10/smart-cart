import pandas as pd
from pymongo import MongoClient
import psycopg2
import re
import os
import glob
from dotenv import load_dotenv
from urllib.parse import quote_plus
from pymongo.errors import ConnectionFailure
import motor.motor_asyncio

# Load environment variables from .env file
load_dotenv()

# Configuration
# Get Credentials securely from environment variables

# PostgreSQL Configuration
POSTGRES_DB_NAME = os.getenv("POSTGRES_DB_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# MongoDB Configuration
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_CLUSTER_NAME = os.getenv('MONGO_CLUSTER_NAME', 'trailcluster')
MONGO_USERNAME = quote_plus(os.getenv('MONGO_USERNAME'))
MONGO_PASSWORD = quote_plus(os.getenv('MONGO_PASSWORD'))
MONGO_URI = f'mongodb+srv://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_CLUSTER_NAME}.f5n8za4.mongodb.net/'
raw_products_collection = os.getenv('MONGO_COLLECTION_RAW_PRODUCTS', 'raw_products')

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

db = client[MONGO_DB_NAME]

# Helper function for data cleaning
def clean_product_data(record):
    '''Cleans a single product record before insertion into PostgreSQL.'''
    # Clean Price to be a number, default to 0.0 if invalid
    try:
        record['price'] = float(record['price'])
        record['original_price'] = float(record['original_price'])
    except (ValueError, TypeError):
        record['price'] = 0.0
        record['original_price'] = 0.0
    
    # Clean Rating to be a number, default to None if invalid
    try:
        rating_match = re.search(r'(d\.\d|\d)', str(record['rating']))
        if rating_match:
            record['rating'] = float(rating_match.group(1))
        else:
            record['rating'] = None
    except (ValueError, TypeError):
        record['rating'] = None

    return record

# Main Execution
if __name__ == "__main__":
    # Find all scrapped CSV Files in the current directory
    csv_files = glob.glob('*_products.csv')
    if not csv_files:
        print("No CSV files found in the current directory.")
        exit()
    print(f"Found {len(csv_files)} CSV files to process.")

    # Load all CSV files into a single DataFrame

    all_products_df = pd.concat([pd.read_csv(file) for file in csv_files], ignore_index=True)
    all_products_records = all_products_df.to_dict('records')
    print(f"Loaded {len(all_products_records)} product records from CSV files.")

    # 1. Populate MongoDB with Raw Product Data
    print("\n-----Connecting to MongoDB...-----")
    try:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        collection = db[raw_products_collection]
        print("Connected to MongoDB successfully.")

        # Clear Existing raw data to avoid duplicates
        print("Clearing existing raw product data in MongoDB...")
        collection.delete_many({})
        print("Existing raw product data cleared.")
        # Clean and insert records into MongoDB
        if all_products_records:
            print("Inserting raw product data into MongoDB...")
            collection.insert_many(all_products_records)
            print(f"Inserted {len(all_products_records)} raw product records into MongoDB.")
        else:
            print("No product records to insert into MongoDB.")
        
        client.close()
        print("MongoDB connection closed.")
        
    except ConnectionFailure as e:
        print(f"Failed to connect to MongoDB: {e}")
        exit()

    # 2. Populate PostgreSQL with Structured Product Data
    print("\n-----Connecting to PostgreSQL...-----")
    try:
        conn = psycopg2.connect(
            dbname = POSTGRES_DB_NAME,
            user = POSTGRES_USER,
            password = POSTGRES_PASSWORD,
            host = POSTGRES_HOST,
            port = POSTGRES_PORT
        )
        cur = conn.cursor()

        print("Connected to PostgreSQL successfully.")

        # Create table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS products (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(255) NOT NULL,
            brand VARCHAR(100),
            price NUMERIC(10, 2),
            original_price NUMERIC(10, 2),
            quantity VARCHAR(50),
            rating NUMERIC (3, 1),
            stock_status VARCHAR(50),
            product_url VARCHAR(512) UNIQUE,
            image_url VARCHAR(512),
            main_category VARCHAR(100),
            sub_category VARCHAR(100),
            sub_category_image_url VARCHAR(512)
        );
        '''
        cur.execute(create_table_query)
        conn.commit()

        print("Products table created or already exists.")
        # Insert cleaned records into PostgreSQL
        print("Inserting cleaned product data into PostgreSQL...")
        insert_count = 0
        for record in all_products_records:
            cleaned_record = clean_product_data(record.copy())
            insert_query = '''
            INSERT INTO products (
            main_category, sub_category, sub_category_image_url, product_name, brand, price, original_price, quantity, rating, stock_status, product_url, image_url
            ) VALUES (
            %(main_category)s, %(sub_category)s, %(sub_category_image_url)s, %(product_name)s, %(brand)s, %(price)s, %(original_price)s, %(quantity)s, %(rating)s, %(stock_status)s, %(product_url)s, %(image_url)s
            ) ON CONFLICT (product_url) DO NOTHING;
            '''

            try:
                cur.execute(insert_query, cleaned_record)
                if cur.rowcount > 0:
                    print(f"Inserted record: {cleaned_record['product_name']}")
                    insert_count += 1
                else:
                    print(f"Record already exists: {cleaned_record['product_name']}")

            except Exception as e:
                print(f"Error inserting record {cleaned_record['product_name']}: {e}")
        
        conn.commit()
        print(f"Inserted {insert_count} product records into PostgreSQL.")

        cur.close()
        conn.close()
        print("PostgreSQL connection closed.")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        exit()

