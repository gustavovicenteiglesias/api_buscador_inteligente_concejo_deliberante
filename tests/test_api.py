import unittest
from main import app
import json

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_chat_validation(self):
        # Envío de body vacío debería dar 400 (capturado por nuestro error_handler)
        response = self.client.post("/api/chat", json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data["code"], "VALIDATION_ERROR")

    def test_admin_deletion_validation(self):
        # Año inválido
        response = self.client.delete("/api/docs/anio/1800")
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
