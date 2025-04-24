import pytest
from unittest.mock import patch
import pymongo
from pymongo.errors import WriteError
import os

from dotenv import dotenv_values

from src.util.dao import DAO

TEST_DATA_VALIDATOR =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["name", "is_male", "email"],
        "properties": {
            "test_value": {
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

TEST_STRING =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["test_data"],
        "properties": {
            "test_data": {
                "bsonType": "string",
                "description": "test data must be string"
            }
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
    def sut_string(self, mock_get_validator, request):
        
        TEST_STRING =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["test_data"],
        "properties": {
            "test_data": {
                "bsonType": "string",
                "description": "test data must be string"
                    }
                }
            }
        }

        mock_get_validator.return_value = TEST_STRING
        sut = DAO(collection_name='test_data')

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values('.env').get('MONGO_URL')
            MONGO_URL = os.environ.get('MONGO_URL', LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection('test_data')

        request.addfinalizer(delete_collection)
        return sut

    @pytest.fixture
    @patch('src.util.dao.getValidator', autospec=True)
    def sut_bool(self, mock_get_validator, request):
        
        TEST_STRING =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["test_data"],
        "properties": {
            "test_data": {
                "bsonType": "bool",
                "description": "test data must be bool"
                    }
                }
            }
        }

        mock_get_validator.return_value = TEST_STRING
        sut = DAO(collection_name='test_data')

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values('.env').get('MONGO_URL')
            MONGO_URL = os.environ.get('MONGO_URL', LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection('test_data')

        request.addfinalizer(delete_collection)
        return sut

    def test_string_string(self, sut_string):
        """Test that an object with the same input data is returned"""
        data = { 'test_data' : 'this is a string'}
        sut_string.create(data)
        validationresult = sut_string.create(data)

        assert data.items() <= validationresult.items()

    def test_string_bool(self, sut_string):
        """Test that an object with the same input data is returned"""
        data = { 'test_data' : True}
        
        with pytest.raises(WriteError, match="type did not match"):
            sut_string.create(data)


    def test_bool_bool(self, sut_bool):
        """Test that an object with the same input data is returned"""
        data = { 'test_data' : True}
        sut_bool.create(data)
        validationresult = sut_bool.create(data)

        assert data.items() <= validationresult.items()

    def test_bool_string(self, sut_bool):
        """Test that an object with the same input data is returned"""
        data = { 'test_data' : "this is a string"}
        
        with pytest.raises(WriteError, match="type did not match"):
            sut_bool.create(data)
