import unittest
from unittest.mock import MagicMock, patch
import sys

# Mocking external dependencies before importing services
sys.modules["weaviate"] = MagicMock()
sys.modules["openai"] = MagicMock()

from app.services.deletion_service import DeletionService
from app.core.errors import ValidationError

class TestServices(unittest.TestCase):
    @patch("app.services.deletion_service.VectorRepository")
    def test_deletion_service_flow(self, mock_repo_class):
        mock_repo = mock_repo_class.return_value
        mock_repo.batch_delete_by_year_month.return_value = {"successful": 10}
        
        service = DeletionService()
        result = service.delete_by_period(2023, 5)
        
        self.assertEqual(result["deleted_count"], 10)
        self.assertEqual(result["status"], "success")

    def test_deletion_validation(self):
        service = DeletionService()
        with self.assertRaises(ValidationError):
            service.delete_by_period(1800)

if __name__ == "__main__":
    unittest.main()
