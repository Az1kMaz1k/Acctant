import sqlite3

class Sqliter:

    def __init__(self, database_file):
        """Connection database"""
        self.connection = sqlite3.connect(database_file)
        self.cursor = self.connection.cursor()


    def new_user(self, user_id, user_name):
        """Add new user"""
        with self.connection:
            return self.cursor.execute("INSERT INTO main (user_id, user_name) VALUES (?,?)",(user_id,user_name))

    def check_user(self,user_id):
        """Check user subcription"""
        with self.connection:
            result = self.cursor.execute("SELECT id FROM main WHERE user_id = ?",(user_id,)).fetchall()
            return bool(len(result))

    def add_company(self,company_name,status,user_id):
        """Add company name for user"""
        with self.connection:
            return self.cursor.execute("UPDATE main SET company_name = ?, status = ? WHERE user_id = ?",(company_name,status,user_id))

    def check_company_name(self,user_id):
        """Check user company name"""
        with self.connection:
            result = self.cursor.execute("SELECT company_name FROM main WHERE user_id = ?",(user_id,)).fetchall()
            return bool(len(result))

    def get_user(self,user_id):
        """Get user info"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM main WHERE user_id = ?", (user_id,)).fetchall()
            return result

    def get_all_user(self):
        """Get all users"""
        with self.connection:
            result = self.cursor.execute("SELECT * FROM main WHERE status = FALSE").fetchall()
            return result

    def close(self):
        """Close connection"""
        self.connection.close()