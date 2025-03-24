import os
import tempfile
import pytest
from test.TestUtils import TestUtils
from legal_document_management_system import load_clients, create_case_document, read_case_document, record_billing, list_case_files


def test_boundary_cases():
    """Test boundary cases for all file operations"""
    # Create temporary files and directories
    temp_dir = tempfile.mkdtemp()
    empty_dir = os.path.join(temp_dir, "empty_dir")
    os.makedirs(empty_dir)
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_client:
        temp_client.write('{"clients": [{"id": "CL001", "name": "", "contact": "", "cases": []}]}')
        client_file = temp_client.name
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_billing:
        temp_billing.write('{"billing": []}')
        billing_file = temp_billing.name
    
    doc_path = os.path.join(temp_dir, "test_doc.txt")
    large_doc_path = os.path.join(temp_dir, "large_doc.txt")
    
    try:
        # Test client data boundary cases
        clients = load_clients(client_file)
        assert 'CL001' in clients, "Client not found"
        assert clients['CL001']['name'] == "", "Empty name not preserved"
        
        # Test document boundary cases
        # Empty content
        create_case_document(doc_path, "Test Doc", "2023-01-01", "Active", "John Doe", "")
        doc_data = read_case_document(doc_path)
        assert doc_data['content'] == "", "Empty content not preserved"
        
        # Large content
        large_content = "A" * 10000
        create_case_document(large_doc_path, "Large Doc", "2023-01-01", "Active", "John Doe", large_content)
        doc_data = read_case_document(large_doc_path)
        assert len(doc_data['content']) == 10000, "Large content not preserved"
        
        # Test billing boundary cases
        # Minimum values
        record_billing(billing_file, "CA001", "2023-01-01", 0.1, 1.0, "Min billing")
        # Large values
        record_billing(billing_file, "CA001", "2023-01-01", 9999.9, 9999.99, "Max billing")
        
        # Test file listing boundary cases
        files = list_case_files(empty_dir)
        assert len(files) == 0, "Empty directory should have 0 files"
        
        # Create test files in temp_dir
        with open(os.path.join(temp_dir, "test1.txt"), 'w') as f:
            f.write("Test file 1")
        with open(os.path.join(temp_dir, "test2.json"), 'w') as f:
            f.write('{"test": true}')
        
        # Test with filters
        files = list_case_files(temp_dir)
        assert len(files) >= 4, "Should list all files"
        
        txt_files = list_case_files(temp_dir, '.txt')
        assert len(txt_files) >= 2, "Should list only text files"
        
        json_files = list_case_files(temp_dir, '.json')
        assert len(json_files) >= 1, "Should list only JSON files"
        
        TestUtils.yakshaAssert("test_boundary_cases", True, "boundary")
    except Exception as e:
        TestUtils.yakshaAssert("test_boundary_cases", False, "boundary")
        raise e
    finally:
        # Clean up
        for file_path in [client_file, billing_file, doc_path, large_doc_path]:
            if os.path.exists(file_path):
                os.remove(file_path)
        
        # Recursively clean directories
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(temp_dir)