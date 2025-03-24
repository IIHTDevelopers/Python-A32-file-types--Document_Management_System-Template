import os
import tempfile
import json
import pytest
from test.TestUtils import TestUtils
from legal_document_management_system import (
    load_clients, 
    add_client, 
    search_clients, 
    read_case_document, 
    create_case_document, 
    record_billing, 
    generate_invoice, 
    create_case_directory, 
    list_case_files, 
    backup_files
)


def test_client_operations():
    """Test basic client operations"""
    # Create a temporary file for client data
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        temp.write('{"clients": []}')
        client_file = temp.name
    
    try:
        # Test adding a client
        add_client(client_file, "CL001", "John Doe", "john.doe@example.com")
        
        # Verify client was added
        clients = load_clients(client_file)
        assert "CL001" in clients, "Client 'CL001' not found in clients"
        assert clients["CL001"]["name"] == "John Doe", "Client name mismatch"
        assert clients["CL001"]["contact"] == "john.doe@example.com", "Client contact mismatch"
        assert "cases" in clients["CL001"], "Client missing 'cases' attribute"
        assert isinstance(clients["CL001"]["cases"], list), "Cases should be a list"
        
        # Add another client
        add_client(client_file, "CL002", "Jane Smith", "jane.smith@example.com")
        
        # Verify second client was added
        clients = load_clients(client_file)
        assert "CL002" in clients, "Client 'CL002' not found in clients"
        
        # Test search functionality (case-insensitive)
        results = search_clients(client_file, "jane")
        assert len(results) == 1, "Search should return exactly one result"
        assert results[0]["id"] == "CL002", "Search returned wrong client"
        
        # Test search with uppercase (testing case-insensitivity)
        results = search_clients(client_file, "JOHN")
        assert len(results) == 1, "Case-insensitive search failed for uppercase term"
        assert results[0]["id"] == "CL001", "Case-insensitive search returned wrong client"
        
        # Test search with no matches
        results = search_clients(client_file, "NonExistent")
        assert len(results) == 0, "Search should return no results"
        
        TestUtils.yakshaAssert("test_client_operations", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_client_operations", False, "functional")
        raise e
    finally:
        os.remove(client_file)


def test_document_operations():
    """Test case document operations"""
    # Create temporary directory for test files
    test_dir = tempfile.mkdtemp()
    doc_path = os.path.join(test_dir, "test_document.txt")
    
    try:
        # Test creating a document
        create_case_document(
            doc_path, 
            "Test Case", 
            "2023-05-10", 
            "Active", 
            "Jane Attorney", 
            "This is a test document content."
        )
        
        # Verify document was created
        assert os.path.exists(doc_path), "Document file was not created"
        
        # Test reading the document
        doc_data = read_case_document(doc_path)
        
        # Verify document metadata and content
        assert "TITLE" in doc_data["metadata"], "Document title metadata missing"
        assert doc_data["metadata"]["TITLE"] == "Test Case", "Document title mismatch"
        assert doc_data["metadata"]["DATE"] == "2023-05-10", "Document date mismatch"
        assert doc_data["metadata"]["STATUS"] == "Active", "Document status mismatch"
        assert doc_data["metadata"]["ATTORNEY"] == "Jane Attorney", "Document attorney mismatch"
        assert doc_data["content"] == "This is a test document content.", "Document content mismatch"
        
        # Test date format validation
        with pytest.raises(ValueError):
            create_case_document(
                os.path.join(test_dir, "invalid_date.txt"),
                "Invalid Date",
                "05/10/2023",  # US format instead of YYYY-MM-DD
                "Active",
                "Jane Attorney",
                "Content"
            )
        
        TestUtils.yakshaAssert("test_document_operations", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_document_operations", False, "functional")
        raise e
    finally:
        # Clean up
        for root, dirs, files in os.walk(test_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
        if os.path.exists(test_dir):
            os.rmdir(test_dir)


def test_billing_operations():
    """Test billing and invoice operations"""
    # Create temporary files for testing
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_billing:
        temp_billing.write('{"billing": []}')
        billing_file = temp_billing.name
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_client:
        client_data = {
            "clients": [
                {
                    "id": "CL001",
                    "name": "John Doe",
                    "contact": "john.doe@example.com",
                    "cases": ["CA001"]
                }
            ]
        }
        json.dump(client_data, temp_client)
        client_file = temp_client.name
    
    invoice_file = tempfile.mktemp()
    
    try:
        # Test recording billing entries
        record_billing(billing_file, "CA001", "2023-05-10", 2.5, 150.0, "Initial consultation")
        record_billing(billing_file, "CA001", "2023-05-15", 3.0, 150.0, "Document preparation")
        
        # Verify billing data was saved
        with open(billing_file, 'r') as file:
            billing_data = json.load(file)
            assert len(billing_data["billing"]) == 2, "Expected 2 billing entries"
            
            # Check first entry details
            assert billing_data["billing"][0]["case_id"] == "CA001", "Case ID mismatch"
            assert billing_data["billing"][0]["hours"] == 2.5, "Hours mismatch"
            assert billing_data["billing"][0]["rate"] == 150.0, "Rate mismatch"
            assert billing_data["billing"][0]["amount"] == 375.0, "Amount mismatch"
            assert billing_data["billing"][0]["description"] == "Initial consultation", "Description mismatch"
        
        # Test generating an invoice
        generate_invoice(billing_file, client_file, "CA001", invoice_file)
        
        # Verify invoice was generated
        assert os.path.exists(invoice_file), "Invoice file was not created"
        
        # Check invoice content
        with open(invoice_file, 'r') as file:
            invoice_content = file.read()
            assert "INVOICE" in invoice_content, "Invoice header missing"
            assert "John Doe" in invoice_content, "Client name missing in invoice"
            assert "CA001" in invoice_content, "Case ID missing in invoice"
            assert "Initial consultation" in invoice_content, "Billing description missing"
            assert "Document preparation" in invoice_content, "Second billing entry missing"
            assert "TOTAL:" in invoice_content, "Total amount missing"
            # Verify total amount matches calculated amount (375.0 + 450.0 = 825.0)
            assert "825.0" in invoice_content.replace(" ", ""), "Invoice amount calculation incorrect"
        
        # Verify case_id validation
        with pytest.raises(ValueError):
            record_billing(billing_file, "INVALID", "2023-05-10", 1.0, 100.0, "Invalid case ID")
        
        TestUtils.yakshaAssert("test_billing_operations", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_billing_operations", False, "functional")
        raise e
    finally:
        for file in [billing_file, client_file, invoice_file]:
            if os.path.exists(file):
                os.remove(file)


def test_file_system_operations():
    """Test file system operations"""
    # Create temporary directory for test files
    base_dir = tempfile.mkdtemp()
    case_id = "CA001"
    
    try:
        # Test creating case directory
        case_dir = create_case_directory(base_dir, case_id)
        
        # Verify directory structure was created
        assert os.path.exists(case_dir), "Case directory was not created"
        assert os.path.exists(os.path.join(case_dir, "documents")), "Documents subdirectory not created"
        assert os.path.exists(os.path.join(case_dir, "billing")), "Billing subdirectory not created"
        
        # Verify info file was created
        info_file = os.path.join(case_dir, f"{case_id}_info.txt")
        assert os.path.exists(info_file), "Case info file not created"
        
        # Create some test files in the case directory and subdirectories
        doc_dir = os.path.join(case_dir, "documents")
        with open(os.path.join(doc_dir, "test_doc1.txt"), 'w') as file:
            file.write("Test document 1")
        with open(os.path.join(doc_dir, "test_doc2.txt"), 'w') as file:
            file.write("Test document 2")
        with open(os.path.join(case_dir, "test.json"), 'w') as file:
            file.write('{"test": true}')
            
        # Create nested directory structure to test recursive search
        nested_dir = os.path.join(doc_dir, "nested")
        os.makedirs(nested_dir)
        with open(os.path.join(nested_dir, "nested_doc.txt"), 'w') as file:
            file.write("Nested document")
        
        # Test listing case files
        all_files = list_case_files(case_dir)
        assert len(all_files) == 5, f"Expected 5 files, found {len(all_files)}"  # Including info file and nested file
        
        # Test filtering by file type
        txt_files = list_case_files(case_dir, ".txt")
        assert len(txt_files) == 4, f"Expected 4 txt files, found {len(txt_files)}"
        
        json_files = list_case_files(case_dir, ".json")
        assert len(json_files) == 1, f"Expected 1 json file, found {len(json_files)}"
        
        # Test path calculation is relative
        assert txt_files[0]['path'] != txt_files[0]['full_path'], "Path should be relative, not full path"
        
        # Verify sorting by modification date
        # Make one file newer than others
        import time
        time.sleep(1)  # Ensure different timestamp
        with open(os.path.join(doc_dir, "newest_file.txt"), 'w') as file:
            file.write("Newest file")
            
        sorted_files = list_case_files(case_dir)
        assert sorted_files[0]['name'] == "newest_file.txt", "Files should be sorted by modification date (newest first)"
        
        # Test backup functionality
        backup_dir = os.path.join(base_dir, "backup")
        backup_count = backup_files(case_dir, backup_dir)
        
        # Verify backup was created
        assert os.path.exists(backup_dir), "Backup directory was not created"
        assert backup_count == 6, f"Expected 6 files backed up, got {backup_count}"
        
        # Verify both txt and json files were backed up
        txt_backups = 0
        json_backups = 0
        for root, _, files in os.walk(backup_dir):
            for filename in files:
                if filename.endswith('.txt'):
                    txt_backups += 1
                elif filename.endswith('.json'):
                    json_backups += 1
        
        assert txt_backups >= 4, "Not all txt files were backed up"
        assert json_backups >= 1, "Not all json files were backed up"
        
        TestUtils.yakshaAssert("test_file_system_operations", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_file_system_operations", False, "functional")
        raise e
    finally:
        # Clean up (recursive delete)
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(base_dir)


def test_complex_workflow():
    """Test a complex workflow combining multiple operations"""
    # Create temporary directories for test files
    base_dir = tempfile.mkdtemp()
    cases_dir = os.path.join(base_dir, "cases")
    os.makedirs(cases_dir)
    
    # Create client and billing files
    client_file = os.path.join(base_dir, "clients.json")
    with open(client_file, 'w') as file:
        file.write('{"clients": []}')
    
    billing_file = os.path.join(base_dir, "billing.json")
    with open(billing_file, 'w') as file:
        file.write('{"billing": []}')
    
    try:
        # 1. Add a client
        add_client(client_file, "CL001", "John Doe", "john.doe@example.com")
        
        # 2. Create a case directory
        case_id = "CA001"
        case_dir = create_case_directory(cases_dir, case_id)
        
        # 3. Update client with case reference
        with open(client_file, 'r') as file:
            data = json.load(file)
        
        for client in data["clients"]:
            if client["id"] == "CL001":
                client["cases"] = [case_id]
        
        with open(client_file, 'w') as file:
            json.dump(data, file)
        
        # 4. Create a case document
        doc_dir = os.path.join(case_dir, "documents")
        doc_path = os.path.join(doc_dir, f"{case_id}_brief.txt")
        create_case_document(
            doc_path,
            "Case Brief",
            "2023-05-01",
            "Active",
            "Jane Attorney",
            "This is a comprehensive case brief for John Doe."
        )
        
        # 5. Record billing entries
        record_billing(billing_file, case_id, "2023-05-01", 2.0, 200.0, "Initial consultation")
        record_billing(billing_file, case_id, "2023-05-10", 5.0, 200.0, "Case research")
        
        # 6. Generate invoice
        invoice_path = os.path.join(case_dir, "invoice.txt")
        generate_invoice(billing_file, client_file, case_id, invoice_path)
        
        # Verify the entire workflow
        # Check client has case
        clients = load_clients(client_file)
        assert "cases" in clients["CL001"], "Client missing cases attribute"
        assert case_id in clients["CL001"]["cases"], "Case not associated with client"
        
        # Check document exists and has correct content
        assert os.path.exists(doc_path), "Case document not created"
        doc_data = read_case_document(doc_path)
        assert doc_data["metadata"]["TITLE"] == "Case Brief", "Document title incorrect"
        
        # Check billing entries
        with open(billing_file, 'r') as file:
            billing_data = json.load(file)
        assert len(billing_data["billing"]) == 2, "Expected 2 billing entries"
        total_amount = sum(entry["amount"] for entry in billing_data["billing"])
        assert total_amount == 1400.0, f"Expected total amount 1400.0, got {total_amount}"
        
        # Check invoice exists and has correct content
        assert os.path.exists(invoice_path), "Invoice not created"
        with open(invoice_path, 'r') as file:
            invoice_content = file.read()
        assert "John Doe" in invoice_content, "Client name missing from invoice"
        assert "1400.0" in invoice_content.replace(" ", ""), "Total amount missing from invoice"
        
        TestUtils.yakshaAssert("test_complex_workflow", True, "functional")
    except Exception as e:
        TestUtils.yakshaAssert("test_complex_workflow", False, "functional")
        raise e
    finally:
        # Clean up (recursive delete)
        for root, dirs, files in os.walk(base_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(base_dir)