import pytest
from unittest.mock import patch
import pymongo
import os

from dotenv import dotenv_values

from src.util.dao import DAO

TEST_DATA_VALIDATOR =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "is_male", "email"],
        "properties": {
            "name": {
                "bsonType": "string",
                "description": "the name must be determined"
            },
            "is_male": {
                "bsonType": "bool",
                "description": "if the person is a male",
                "uniqueItems": True
            },

        }
    }
}

class TestDaoCreate:
    """Creating a fixture to add a new collection and then deleting it after the test
    is done. The data structure checkup in DAO is done by getValidator, which we
    mock here so that it returns our own validator (TEST_DATA_VALIDATOR).
    """
    @pytest.fixture
    @patch('src.util.dao.getValidator', autospec=True)
    def sut(self, mock_get_validator, request):
        mock_get_validator.return_value = TEST_DATA_VALIDATOR
        sut = DAO(collection_name='test_data')

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values('.env').get('MONGO_URL')
            MONGO_URL = os.environ.get('MONGO_URL', LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection('test_data')

        request.addfinalizer(delete_collection)
        return sut

    def test_CreateReturn(self, sut):
        """Test that an object with the same input data is returned"""
        data = { 'name' : 'Sven', 'is_male' : True, 'email' : "swen2"}
        sut.create(data)
        validationresult = sut.create(data)

        assert data.items() <= validationresult.items()
    
    def test_validateCreate(self, sut):
        data = { 'name' : 'Sven', 'is_male' : True, 'email' : "swen"}
        validationresult = sut.create(data)
        
        assert data.items() <= validationresult.items()