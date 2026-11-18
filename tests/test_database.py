
import unittest
import sqlite3

from src.database import DatabaseRepository


class TestDatabaseRepository(unittest.TestCase):

    def setUp(self):
        self.repository = DatabaseRepository(":memory:")

    def tearDown(self):
        self.repository.close()

    # ADD

    def test_add_success(self):
        result = self.repository.add(
            1, "ivan", "Привет!"
        )

        self.assertTrue(result)

        comment = self.repository.get_by_id(1)

        self.assertEqual(comment["name"], "ivan")

    def test_add_duplicate_id(self):
        self.repository.add(1, "ivan", "Первое сообщение")

        with self.assertRaises(sqlite3.IntegrityError):
            self.repository.add(
                1, "alex", "Второе сообщение"
            )

    # GET BY ID

    def test_get_by_id_success(self):
        self.repository.add(1, "ivan", "Привет!")

        result = self.repository.get_by_id(1)

        self.assertIsNotNone(result)
        self.assertEqual(result["message"], "Привет!")

    def test_get_by_id_not_found(self):
        result = self.repository.get_by_id(999)

        self.assertIsNone(result)

    # GET BY NAME

    def test_get_by_name_success(self):
        self.repository.add(1, "ivan", "Сообщение 1")
        self.repository.add(2, "ivan", "Сообщение 2")
        self.repository.add(3, "alex", "Сообщение 3")

        result = self.repository.get_by_name("ivan")

        self.assertEqual(len(result), 2)

    def test_get_by_name_not_found(self):
        result = self.repository.get_by_name("unknown")

        self.assertEqual(result, [])

    # UPDATE

    def test_update_success(self):
        self.repository.add(1, "ivan", "Старый текст")

        result = self.repository.update(
            1, "Новый текст"
        )

        self.assertTrue(result)

        comment = self.repository.get_by_id(1)

        self.assertEqual(
            comment["message"],
            "Новый текст"
        )

    def test_update_not_found(self):
        result = self.repository.update(
            999, "Новый текст"
        )

        self.assertFalse(result)

    # DELETE

    def test_delete_success(self):
        self.repository.add(1, "ivan", "Привет!")

        result = self.repository.delete(1)

        self.assertTrue(result)
        self.assertIsNone(self.repository.get_by_id(1))

    def test_delete_not_found(self):
        result = self.repository.delete(999)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
