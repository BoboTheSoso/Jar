#Python database management commands
import sqlite3
db_path = 'jar.db' #path to the SQLite database file


def get_connection():
    return sqlite3.connect(db_path) #function to get a connection to the database

#initialize database
def initialize_database():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS jar (
                dollar INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER NOT NULL,
                assigned_to INTEGER NOT NULL,
                submission_by INTEGER NOT NULL,
                label TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('CREATE INDEX IF NOT EXISTS idx_guild_id ON jar (guild_id)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_assigned_to ON jar (assigned_to)')
        c.execute('CREATE INDEX IF NOT EXISTS idx_submission_by ON jar (submission_by)')
        conn.commit() #commit the changes to the database


#adding a dollar to the databse:
def add_dollar(guild_id, assigned_to, submission_by, label):
    conn = get_connection() #connect to the database
    c = conn.cursor() #create a cursor object to execute SQL commands

    c.execute('''
                   INSERT INTO jar (guild_id, assigned_to, submission_by, label)
                   VALUES (?, ?, ?, ?)
                   ''', (guild_id, assigned_to, submission_by, label))
    conn.commit() #commit the changes to the database
    conn.close() #close the connection to the database

#pulling all dollars for a specific guild+user:
def pull_user_dollars(guild_id, assigned_to):
    conn = get_connection() #connect to the database
    c = conn.cursor() #create a cursor object to execute SQL commands

    c.execute('''
                   SELECT * FROM jar
                   WHERE guild_id = ? AND assigned_to = ?
                   ''', (guild_id, assigned_to))
    dollars = c.fetchall() #fetch all matching records
    conn.close() #close the connection to the database
    return dollars #return the list of dollars

#pull all dollars submitted by a specific user in a guild:
def pull_submitted_dollars(guild_id, submission_by):
    conn = get_connection() #connect to the database
    c = conn.cursor() #create a cursor object to execute SQL commands

    c.execute('''
                   SELECT * FROM jar
                   WHERE guild_id = ? AND submission_by = ?
                   ''', (guild_id, submission_by))
    dollars = c.fetchall() #fetch all matching records
    conn.close() #close the connection to the database
    return dollars #return the list of dollars

#get dollar amount for a specific guild+user:
def get_dollar_amount(guild_id, assigned_to):
    conn = get_connection() #connect to the database
    c = conn.cursor() #create a cursor object to execute SQL commands

    c.execute('''
                   SELECT COUNT(*) FROM jar
                   WHERE guild_id = ? AND assigned_to = ?
                   ''', (guild_id, assigned_to))
    amount = c.fetchone()[0] #fetch the count result
    conn.close() #close the connection to the database
    return amount #return the dollar amount

#get top 5 dollar amounts per user for a guild
def get_top_5_dollars(guild_id):
    conn = get_connection() #connect to the database
    c = conn.cursor() #create a cursor object to execute SQL commands

    c.execute('''
                   SELECT assigned_to, COUNT(*) as dollar_count FROM jar
                   WHERE guild_id = ?
                   GROUP BY assigned_to
                   ORDER BY dollar_count DESC
                   LIMIT 5
                   ''', (guild_id,))
    top_users = c.fetchall() #fetch all matching records
    conn.close() #close the connection to the database
    return top_users #return the list of top users and their dollar counts
