
import sqlite3


class DatabaseRepository:
    def __init__(self, db_path="comments.db"):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row

        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL CHECK(length(name) <= 256),
                message TEXT NOT NULL CHECK(length(message) <= 8096)
            )
        """)
        self.connection.commit()

    def _validate_id(self, comment_id):
        if type(comment_id) is not int:
            raise TypeError("ID должен быть целым числом")

    def _validate_text(self, username, message):
        if not isinstance(username, str):
            raise TypeError("Имя пользователя должно быть строкой")

        if not isinstance(message, str):
            raise TypeError("Сообщение должно быть строкой")

        if len(username) > 256:
            raise ValueError("Имя пользователя длиннее 256 символов")

        if len(message) > 8096:
            raise ValueError("Сообщение длиннее 8096 символов")

    def get_by_id(self, comment_id: int):
        self._validate_id(comment_id)

        cursor = self.connection.execute(
            "SELECT * FROM comments WHERE id = ?",
            (comment_id,)
        )

        row = cursor.fetchone()
        return dict(row) if row else None

    def get_by_name(self, username: str):
        if not isinstance(username, str):
            raise TypeError("Имя пользователя должно быть строкой")

        cursor = self.connection.execute(
            "SELECT * FROM comments WHERE name = ?",
            (username,)
        )

        return [dict(row) for row in cursor.fetchall()]

    def add(self, comment_id: int, username: str, message: str):
        self._validate_id(comment_id)
        self._validate_text(username, message)

        self.connection.execute(
            """
            INSERT INTO comments (id, name, message)
            VALUES (?, ?, ?)
            """,
            (comment_id, username, message)
        )

        self.connection.commit()
        return True

    def update(self, comment_id: int, new_message: str):
        self._validate_id(comment_id)

        if not isinstance(new_message, str):
            raise TypeError("Сообщение должно быть строкой")

        if len(new_message) > 8096:
            raise ValueError("Сообщение длиннее 8096 символов")

        cursor = self.connection.execute(
            """
            UPDATE comments
            SET message = ?
            WHERE id = ?
            """,
            (new_message, comment_id)
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def delete(self, comment_id: int):
        self._validate_id(comment_id)

        cursor = self.connection.execute(
            "DELETE FROM comments WHERE id = ?",
            (comment_id,)
        )

        self.connection.commit()
        return cursor.rowcount > 0

    def close(self):
        self.connection.close()
