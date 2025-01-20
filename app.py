from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Request
import mysql.connector
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

mysql_host = os.getenv("MYSQL_HOST")
mysql_user = os.getenv("MYSQL_USER")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_database = os.getenv("MYSQL_DATABASE")
mysql_port = int(os.getenv("MYSQL_PORT", 3306))

# SSL certificate paths
SSL_CA_PATH = "/etc/mysql/ssl/cloudways_ca.crt"
SSL_CERT_PATH = "/etc/mysql/ssl/mysql_server.crt"
SSL_KEY_PATH = "/etc/mysql/ssl/mysql_server.key"

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def create_mysql_connection():
    return mysql.connector.connect(
        host=mysql_host,
        user=mysql_user,
        password=mysql_password,
        database=mysql_database,
        port=mysql_port,
        ssl_ca=SSL_CA_PATH,      # SSL CA Certificate
        ssl_cert=SSL_CERT_PATH,  # SSL Server Certificate
        ssl_key=SSL_KEY_PATH     # SSL Private Key
    )

@app.get("/sqlquery/")
async def sqlquery(sqlquery: str):
    try:
        connection = create_mysql_connection()
        cursor = connection.cursor()
        cursor.execute(sqlquery)
        
        # Handle queries that return results
        if cursor.description is not None:
            headers = [i[0] for i in cursor.description]
            results = cursor.fetchall()
            return {"headers": headers, "results": results}
        else:
            connection.commit()
            return {"status": "Query executed successfully"}
    except mysql.connector.Error as e:
        logger.error(f"MySQL error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"MySQL error: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
