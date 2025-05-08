import pytest
from unittest.mock import Mock

from src.controllers.usercontroller import UserController

class TestUserController:
    """Tests for the UserController get_user_by_email method."""

    @pytest.fixture
    def controller(self):
        mock_dao = Mock()
        return UserController(dao=mock_dao), mock_dao
    
    @pytest.mark.useremail
    def test_valid_single_user(self, controller):
        # Arrange
        uc, mock_dao = controller
        test_email = "valid@example.com"
        test_user = {"id": "123", "email": test_email}
        mock_dao.find.return_value = [test_user]
        
        # Act
        result = uc.get_user_by_email(test_email)
        
        # Assert
        assert result == test_user
    
    @pytest.mark.useremail
    def test_valid_multiple_users(self, controller):
        # Arrange
        uc, mock_dao = controller
        test_email = "duplicate@example.com"
        user1 = {"id": "123", "email": test_email}
        user2 = {"id": "456", "email": test_email}
        mock_dao.find.return_value = [user1, user2]
        
        # Act
        result = uc.get_user_by_email(test_email)
        
        # Assert
        assert result == user1
    
    @pytest.mark.useremail
    def test_valid_no_users(self, controller):
        # Arrange
        uc, mock_dao = controller
        test_email = "nonexistent@example.com"
        mock_dao.find.return_value = []
        
        # Act
        result = uc.get_user_by_email(test_email)
        
        # Assert
        assert result is None
    
    @pytest.mark.useremail
    def test_invalid_email(self, controller):
        # Arrange
        uc, mock_dao = controller
        invalid_email = "not-an-email"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Error: invalid email address"):
            uc.get_user_by_email(invalid_email)