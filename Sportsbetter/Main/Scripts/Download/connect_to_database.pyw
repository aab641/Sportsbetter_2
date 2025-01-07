
import psycopg2

# Connect to your PostgreSQL database
connection = psycopg2.connect(
    dbname="Seabed_sports_betting_database",
    user="postgres",
    password="Vortex1996??",
    host="localhost",
    port="5432"
)

cursor = connection.cursor()

# Test the connection
cursor.execute("SELECT version();")
print("Connected to:", cursor.fetchone())

# Close the connection
cursor.close()
connection.close()
