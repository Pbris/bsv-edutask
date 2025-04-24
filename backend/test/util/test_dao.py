import pytest
from unittest.mock import patch
import pymongo
from pymongo.errors import WriteError
import os

from dotenv import dotenv_values

from src.util.dao import DAO


class TestDaoCreate:
    """Creating a fixture to add a new collection and then deleting it after the test
    is done. The data structure checkup in DAO is done by getValidator, which we
    mock here so that it returns our own validator (TEST_DATA_VALIDATOR).
    """
    @pytest.fixture
    @patch("src.util.dao.getValidator", autospec=True)
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
        sut = DAO(collection_name="test_data")

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values(".env").get("MONGO_URL")
            MONGO_URL = os.environ.get("MONGO_URL", LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection("test_data")

        request.addfinalizer(delete_collection)
        return sut

    @pytest.fixture
    @patch("src.util.dao.getValidator", autospec=True)
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
        sut = DAO(collection_name="test_data")

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values(".env").get("MONGO_URL")
            MONGO_URL = os.environ.get("MONGO_URL", LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection("test_data")

        request.addfinalizer(delete_collection)
        return sut


    @pytest.fixture
    @patch("src.util.dao.getValidator", autospec=True)
    def sut_required(self, mock_get_validator, request):
        
        TEST_STRING =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["test_data"],
        "properties": {
            "test_data": {
                "description": "test data must exist"
                    }
                }
            }
        }

        mock_get_validator.return_value = TEST_STRING
        sut = DAO(collection_name="test_data")

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values(".env").get("MONGO_URL")
            MONGO_URL = os.environ.get("MONGO_URL", LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection("test_data")

        request.addfinalizer(delete_collection)
        return sut

    @pytest.fixture
    @patch("src.util.dao.getValidator", autospec=True)
    def sut_unique(self, mock_get_validator, request):
        
        TEST_STRING =  {
        "$jsonSchema": {
        "bsonType": "object",
        "required": ["test_data"],
        "properties": {
            "test_data": {
                "description": "test data must be unique",
                "uniqueItems": True
                    }
                }
            }
        }

        mock_get_validator.return_value = TEST_STRING
        sut = DAO(collection_name="test_data")

        def delete_collection():
            LOCAL_MONGO_URL = dotenv_values(".env").get("MONGO_URL")
            MONGO_URL = os.environ.get("MONGO_URL", LOCAL_MONGO_URL)
            client = pymongo.MongoClient(MONGO_URL)
            database = client.edutask
            database.drop_collection("test_data")

        request.addfinalizer(delete_collection)
        return sut

    def test_string_string(self, sut_string):
        """Test that a String object returns an object that contains the input data"""
        data = { "test_data" : "this is a string"}
        sut_string.create(data)
        validationresult = sut_string.create(data)

        assert data.items() <= validationresult.items()

    def test_string_bool(self, sut_string):
        """Test that a WriteError is raised when the data type 
        should be String, but isn't, according the validation schema.
        """
        data = { "test_data" : True}
        
        with pytest.raises(WriteError, match="type did not match"):
            sut_string.create(data)


    def test_bool_bool(self, sut_bool):
        """Test that a Boolean object returns an object that contains the input data"""
        data = { "test_data" : True}
        validationresult = sut_bool.create(data)

        assert data.items() <= validationresult.items()

    def test_bool_string(self, sut_bool):
        """Test that a WriteError is raised when the data type 
        should be Bool, but isn't, according the validation schema.
        """
        data = { "test_data" : "this is a string"}
        
        with pytest.raises(WriteError, match="type did not match"):
            sut_bool.create(data)

    def test_required_exists(self, sut_required):
        """Test that an object with the same input data is returned when the required field exists"""
        data = {"test_data" : "any value"}
        validationresult = sut_required.create(data)

        assert data.items() <= validationresult.items()

    def test_required_does_not_exist(self, sut_required):
        """Test that an error is raised when the required field does not exist"""
        data = {}

        with pytest.raises(WriteError, match="missingProperties"):
            sut_required.create(data)

    def test_data_is_unique(self, sut_unique):
        """Test that an object with the same input data is returned when the field is unique exists"""
        data = {"test_data" : "any value"}

        validationresult = sut_unique.create(data)

        assert data.items() <= validationresult.items()

    def test_data_is_not_unique(self, sut_unique):
        """Test that a WriteError is raised when the data is not unique"""
        data = {"test_data" : "any value"}
        with pytest.raises(WriteError, match="duplicatedValue"):
            sut_unique.create(data)
            sut_unique.create(data) # This should raise an error since the data is not unique

