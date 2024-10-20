# models.py
from cassandra.cluster import Cluster

# Подключение к кластеру Cassandra
cluster = Cluster(["127.0.0.1"])  # IP вашего кластера Cassandra
session = cluster.connect()

# Создание keyspace и таблиц
session.execute("""
    CREATE KEYSPACE IF NOT EXISTS secret_storage 
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 1}
""")
session.set_keyspace("secret_storage")

# Таблица для секретов
session.execute("""
    CREATE TABLE IF NOT EXISTS secrets (
        id UUID PRIMARY KEY,
        value text,
        type text,
        owner text,
        namespace text
    )
""")

# Таблица для версий секретов
session.execute("""
    CREATE TABLE IF NOT EXISTS secret_versions (
        version_id UUID PRIMARY KEY,
        secret_id UUID,
        value text,
        type text,
        owner text,
        created_at timestamp
    )
""")

# Таблица для динамических секретов с TTL
session.execute("""
    CREATE TABLE IF NOT EXISTS dynamic_secrets (
        id UUID PRIMARY KEY,
        value text,
        type text,
        owner text,
        ttl timestamp
    )
""")

# Таблица для неймспейсов
session.execute("""
    CREATE TABLE IF NOT EXISTS namespaces (
        namespace_id UUID PRIMARY KEY,
        namespace_name text,
        owner text
    )
""")
