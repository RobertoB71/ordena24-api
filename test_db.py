from database.database import engine

try:
    with engine.connect() as connection:
        print("Conexión exitosa a PostgreSQL")
except Exception as error:
    print("Error al conectar con PostgreSQL:")
    print(error)