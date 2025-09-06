import unittest
from src.services.yandex_client import YandexClient

class TestYandexClient(unittest.TestCase):

    def setUp(self):
        self.client = YandexClient()

    def test_get_response(self):
        user_input = "Привет, как дела?"
        response = self.client.get_response(user_input)
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_invalid_input(self):
        user_input = ""
        response = self.client.get_response(user_input)
        self.assertEqual(response, "Ошибка: пустой ввод")

if __name__ == '__main__':
    unittest.main()