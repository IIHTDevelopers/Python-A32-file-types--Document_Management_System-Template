import os
import json
import tempfile
import pytest
from test.TestUtils import TestUtils
from legal_document_management_system import (
    load_clients, 
    add_client, 
    create_case_document, 
    record_billing, 
    create_case_directory, 
    generate_invoice,
    list_case_files
)


def test_file_operations_exceptions():
    """Test file not found and format exceptions for all operations"""
    # Create temporary test files/directories
    non_existent_file = "non_existent_file_" + os.urandom(8).hex() + ".json"
    test_dir = tempfile.mkdtemp()
    non_existent_dir = os.path.join(test_dir, "non_existent_dir")
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_json:
        temp_json.write('{"clients": [{"id": "CL001", "name": "Test"')  # Invalid JSON
        invalid_json_file = temp_json.name
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_client:
        temp_client.write('{"clients": []}')
        client_file = temp_client.name
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_billing:
        temp_billing.write('{"billing": []}')
        billing_file = temp_billing.name
    
    doc_path = os.path.join(test_dir, "test_doc.txt")
    
    try:
        # Test file not found exceptions
        with pytest.raises(FileNotFoundError):
            load_clients(non_existent_file)
        
        with pytest.raises(FileNotFoundError):
            list_case_files(non_existent_dir)
        
        # Test invalid JSON format
        with pytest.raises(json.JSONDecodeError):
            load_clients(invalid_json_file)
        
        # Test client data validation
        with pytest.raises(ValueError):
            add_client(client_file, "001", "Test Client", "test@example.com")  # Invalid ID format
            
        with pytest.raises(ValueError):
            add_client(client_file, "CLABC", "Test Client", "test@example.com")  # Non-numeric suffix
            
        with pytest.raises(ValueError):
            add_client(client_file, "CL001", "", "test@example.com")  # Empty name
        
        # Test document creation validation
        with pytest.raises(ValueError):
            create_case_document(doc_path, "Test", "01/01/2023", "Active", "John", "Content")  # Invalid date format
        
        # Test billing validation
        with pytest.raises(ValueError):
            record_billing(billing_file, "CA001", "2023-01-01", -1.0, 100.0, "Billing")  # Negative hours
            
        with pytest.raises(ValueError):
            record_billing(billing_file, "CA001", "2023-01-01", 1.0, 0.0, "Billing")  # Zero rate
            
        with pytest.raises(ValueError):
            record_billing(billing_file, "CA001", "2023-01-01", "one", 100.0, "Billing")  # Non-numeric hours
        
        # Test case directory validation
        with pytest.raises(ValueError):
            create_case_directory(test_dir, "001")  # Invalid case ID format
            
        with pytest.raises(ValueError):
            create_case_directory(test_dir, "")  # Empty case ID
        
        TestUtils.yakshaAssert("test_file_operations_exceptions", True, "exceptional")
    except Exception as e:
        TestUtils.yakshaAssert("test_file_operations_exceptions", False, "exceptional")
        raise e
    finally:
        # Clean up temporary files
        for file_path in [invalid_json_file, client_file, billing_file]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Recursively clean directories
        for root, dirs, files in os.walk(test_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        if os.path.exists(test_dir):
            os.rmdir(test_dir)