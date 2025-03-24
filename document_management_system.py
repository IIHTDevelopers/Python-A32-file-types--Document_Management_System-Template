"""
Document Management System

This module implements a document management system for a legal office
to handle various file types including JSON data files and text documents.
"""

import os
import json
import datetime
import shutil


def load_clients(file_path):
   """
   Read client data from a JSON file.
   
   Args:
       file_path: Path to the clients JSON file
       
   Returns:
       Dictionary of client objects indexed by client ID
       
   Raises:
       FileNotFoundError: If the file does not exist
       json.JSONDecodeError: If the file contains invalid JSON
   """
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"Clients file not found: {file_path}")
   
   with open(file_path, 'r', encoding='utf-8') as file:
       try:
           data = json.load(file)
           clients = {}
           
           for client in data.get('clients', []):
               client_id = client.get('id')
               clients[client_id] = {
                   'name': client.get('name', ''),
                   'contact': client.get('contact', ''),
                   'cases': client.get('cases', [])
               }
               
           return clients
       except json.JSONDecodeError as e:
           raise json.JSONDecodeError(f"Invalid JSON format: {e.msg}", e.doc, e.pos)


def add_client(file_path, client_id, name, contact):
   """
   Add a new client to the JSON file.
   
   Args:
       file_path: Path to the clients JSON file
       client_id: Client ID (format: CL followed by 3 digits)
       name: Client name
       contact: Client contact information
       
   Returns:
       Boolean indicating success
   """
   # Validate client ID format
   if not client_id or not client_id.startswith('CL') or not client_id[2:].isdigit():
       raise ValueError("Client ID must be in format 'CLXXX' where X is a digit")
   
   # Validate name is not empty
   if not name:
       raise ValueError("Client name cannot be empty")
   
   # Load existing data or create new structure
   data = {'clients': []}
   if os.path.exists(file_path):
       try:
           with open(file_path, 'r', encoding='utf-8') as file:
               data = json.load(file)
       except json.JSONDecodeError:
           pass
   
   # Add new client
   data['clients'].append({
       'id': client_id,
       'name': name,
       'contact': contact,
       'cases': []
   })
   
   # Write updated data back to file
   with open(file_path, 'w', encoding='utf-8') as file:
       json.dump(data, file, indent=2)
   
   return True


def search_clients(file_path, search_term):
   """
   Search for clients matching the search term.
   
   Args:
       file_path: Path to the clients JSON file
       search_term: Term to search for in client data
       
   Returns:
       List of matching client records
   """
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"Clients file not found: {file_path}")
   
   search_term = search_term.lower()
   results = []
   
   with open(file_path, 'r', encoding='utf-8') as file:
       data = json.load(file)
       
       for client in data.get('clients', []):
           client_text = json.dumps(client).lower()
           if search_term in client_text:
               results.append(client)
       
       return results


def read_case_document(file_path):
   """
   Read and parse a case document file.
   
   Args:
       file_path: Path to the case document file
       
   Returns:
       Dictionary with metadata and content sections
   """
   if not os.path.exists(file_path):
       raise FileNotFoundError(f"Document not found: {file_path}")
   
   with open(file_path, 'r', encoding='utf-8') as file:
       content = file.read()
       
       # Split metadata and document content
       if '---' in content:
           parts = content.split('---', 1)
           metadata_text = parts[0].strip()
           document_content = parts[1].strip() if len(parts) > 1 else ""
           
           # Parse metadata
           metadata = {}
           for line in metadata_text.split('\n'):
               if ':' in line:
                   key, value = line.split(':', 1)
                   metadata[key.strip()] = value.strip()
           
           return {
               'metadata': metadata,
               'content': document_content
           }
       else:
           return {
               'metadata': {},
               'content': content
           }


def create_case_document(file_path, title, date, status, attorney, content):
   """
   Create a new case document with metadata.
   
   Args:
       file_path: Path where the document will be saved
       title: Case title
       date: Case date (YYYY-MM-DD format)
       status: Case status
       attorney: Assigned attorney
       content: Document content
   """
   # Validate date format
   try:
       datetime.datetime.strptime(date, '%Y-%m-%d')
   except ValueError:
       raise ValueError("Date must be in YYYY-MM-DD format")
   
   # Format document with metadata
   document = f"TITLE: {title}\nDATE: {date}\nSTATUS: {status}\nATTORNEY: {attorney}\n---\n{content}"
   
   # Write to file
   with open(file_path, 'w', encoding='utf-8') as file:
       file.write(document)


def record_billing(file_path, case_id, date, hours, rate, description):
   """
   Record a billing entry in the JSON billing file.
   
   Args:
       file_path: Path to the billing JSON file
       case_id: Case ID
       date: Billing date (YYYY-MM-DD format)
       hours: Hours worked
       rate: Hourly rate
       description: Description of the work performed
   """
   # Validate case ID format
   if not case_id or not case_id.startswith('CA') or not case_id[2:].isdigit():
       raise ValueError("Case ID must be in format 'CAXXX' where X is a digit")
   
   # Validate numeric values
   hours = float(hours)
   rate = float(rate)
   if hours <= 0 or rate <= 0:
       raise ValueError("Hours and rate must be positive numbers")
   
   # Calculate total amount
   amount = round(hours * rate, 2)
   
   # Load existing data or create new structure
   data = {'billing': []}
   if os.path.exists(file_path):
       try:
           with open(file_path, 'r', encoding='utf-8') as file:
               data = json.load(file)
       except json.JSONDecodeError:
           pass
   
   # Add new billing entry
   data['billing'].append({
       'case_id': case_id,
       'date': date,
       'hours': hours,
       'rate': rate,
       'amount': amount,
       'description': description
   })
   
   # Write updated data back to file
   with open(file_path, 'w', encoding='utf-8') as file:
       json.dump(data, file, indent=2)
       
       
def record_billing(file_path, case_id, date, hours, rate, description):
   """
   Record a billing entry in the JSON billing file.
   
   Args:
       file_path: Path to the billing JSON file
       case_id: Case ID
       date: Billing date (YYYY-MM-DD format)
       hours: Hours worked
       rate: Hourly rate
       description: Description of the work performed
   """
   # Validate case ID format
   if not case_id or not case_id.startswith('CA') or not case_id[2:].isdigit():
       raise ValueError("Case ID must be in format 'CAXXX' where X is a digit")
   
   # Validate numeric values
   hours = float(hours)
   rate = float(rate)
   if hours <= 0 or rate <= 0:
       raise ValueError("Hours and rate must be positive numbers")
   
   # Calculate total amount
   amount = round(hours * rate, 2)
   
   # Load existing data or create new structure
   data = {'billing': []}
   if os.path.exists(file_path):
       try:
           with open(file_path, 'r', encoding='utf-8') as file:
               data = json.load(file)
       except json.JSONDecodeError:
           pass
   
   # Add new billing entry
   data['billing'].append({
       'case_id': case_id,
       'date': date,
       'hours': hours,
       'rate': rate,
       'amount': amount,
       'description': description
   })
   
   # Write updated data back to file
   with open(file_path, 'w', encoding='utf-8') as file:
       json.dump(data, file, indent=2)


def generate_invoice(billing_file, client_file, case_id, output_file):
   """
   Generate an invoice for a specific case.
   
   Args:
       billing_file: Path to the billing JSON file
       client_file: Path to the clients JSON file
       case_id: Case ID to generate invoice for
       output_file: Path where the invoice will be saved
   """
   # Check if files exist
   if not os.path.exists(billing_file) or not os.path.exists(client_file):
       raise FileNotFoundError("Required files not found")
   
   # Load billing data
   with open(billing_file, 'r', encoding='utf-8') as file:
       billing_data = json.load(file)
   
   # Filter billing entries for the specified case
   case_entries = [entry for entry in billing_data.get('billing', []) 
                  if entry.get('case_id') == case_id]
   
   # Find client for this case
   client_info = None
   with open(client_file, 'r', encoding='utf-8') as file:
       client_data = json.load(file)
       
       for client in client_data.get('clients', []):
           if case_id in client.get('cases', []):
               client_info = client
               break
   
   if not client_info:
       client_info = {"name": "Unknown Client", "id": "Unknown", "contact": ""}
   
   # Calculate totals
   total_hours = sum(entry.get('hours', 0) for entry in case_entries)
   total_amount = sum(entry.get('amount', 0) for entry in case_entries)
   
   # Generate invoice text
   invoice_date = datetime.datetime.now().strftime('%Y-%m-%d')
   invoice_text = f"INVOICE\n\n"
   invoice_text += f"Date: {invoice_date}\n"
   invoice_text += f"Case ID: {case_id}\n"
   invoice_text += f"Client: {client_info.get('name')} ({client_info.get('id')})\n\n"
   
   invoice_text += "BILLING DETAILS\n"
   invoice_text += "-" * 80 + "\n"
   
   for entry in case_entries:
       date = entry.get('date', '')
       hours = entry.get('hours', 0)
       amount = entry.get('amount', 0)
       desc = entry.get('description', '')
       
       invoice_text += f"{date} - {hours} hrs - ${amount:.2f} - {desc}\n"
   
   invoice_text += "-" * 80 + "\n"
   invoice_text += f"TOTAL: {total_hours} hours, ${total_amount:.2f}\n"
   
   # Write invoice to file
   with open(output_file, 'w', encoding='utf-8') as file:
       file.write(invoice_text)


def create_case_directory(base_path, case_id):
   """
   Create a directory structure for a new case.
   
   Args:
       base_path: Base directory path
       case_id: Case ID
       
   Returns:
       Path to the created case directory
   """
   # Validate case ID format
   if not case_id or not case_id.startswith('CA') or not case_id[2:].isdigit():
       raise ValueError("Case ID must be in format 'CAXXX' where X is a digit")
   
   # Create case directory path
   case_dir = os.path.join(base_path, case_id)
   
   # Create main directory and subdirectories
   os.makedirs(case_dir, exist_ok=True)
   os.makedirs(os.path.join(case_dir, 'documents'), exist_ok=True)
   os.makedirs(os.path.join(case_dir, 'billing'), exist_ok=True)
   
   # Create empty case info file
   info_file = os.path.join(case_dir, f"{case_id}_info.txt")
   with open(info_file, 'w', encoding='utf-8') as file:
       file.write(f"CASE: {case_id}\n")
       file.write(f"CREATED: {datetime.datetime.now().strftime('%Y-%m-%d')}\n")
       file.write("STATUS: New\n")
       file.write("---\n")
   
   return case_dir


def list_case_files(case_path, file_type=None):
   """
   List all files in a case directory, optionally filtered by type.
   
   Args:
       case_path: Path to the case directory
       file_type: Optional file extension to filter by (e.g., '.txt')
       
   Returns:
       List of dictionaries with file information
   """
   if not os.path.exists(case_path):
       raise FileNotFoundError(f"Case directory not found: {case_path}")
   
   result = []
   
   # Walk through all subdirectories
   for root, _, files in os.walk(case_path):
       for filename in files:
           # Apply file type filter if specified
           if file_type and not filename.endswith(file_type):
               continue
               
           file_path = os.path.join(root, filename)
           rel_path = os.path.relpath(file_path, case_path)
           
           # Get file metadata
           file_info = {
               'name': filename,
               'path': rel_path,
               'full_path': file_path,
               'size': os.path.getsize(file_path),
               'modified': datetime.datetime.fromtimestamp(
                   os.path.getmtime(file_path)
               ).strftime('%Y-%m-%d %H:%M:%S')
           }
           
           result.append(file_info)
   
   # Sort by modification date (newest first)
   result.sort(key=lambda x: x['modified'], reverse=True)
   
   return result


def backup_files(source_dir, backup_dir):
   """
   Create backups of important files.
   
   Args:
       source_dir: Source directory
       backup_dir: Backup directory
       
   Returns:
       Number of files backed up
   """
   if not os.path.exists(source_dir):
       raise FileNotFoundError(f"Source directory not found: {source_dir}")
   
   if not os.path.exists(backup_dir):
       os.makedirs(backup_dir)
   
   timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
   count = 0
   
   for root, _, files in os.walk(source_dir):
       for filename in files:
           if filename.endswith(('.json', '.txt')):
               source_path = os.path.join(root, filename)
               rel_path = os.path.relpath(root, source_dir)
               
               # Create subdirectory in backup if needed
               backup_subdir = os.path.join(backup_dir, rel_path)
               os.makedirs(backup_subdir, exist_ok=True)
               
               # Create backup filename
               backup_name = f"{os.path.splitext(filename)[0]}_{timestamp}{os.path.splitext(filename)[1]}"
               backup_path = os.path.join(backup_subdir, backup_name)
               
               # Copy file
               shutil.copy2(source_path, backup_path)
               count += 1
   
   return count


def main():
   """
   Main function providing a menu-driven interface for the document management system.
   """
   # Define file paths and directories
   base_dir = "legal_office_data"
   if not os.path.exists(base_dir):
       os.makedirs(base_dir)
   
   clients_file = os.path.join(base_dir, "clients.json")
   billing_file = os.path.join(base_dir, "billing.json")
   cases_dir = os.path.join(base_dir, "cases")
   backup_dir = os.path.join(base_dir, "backups")
   
   # Create required directories
   os.makedirs(cases_dir, exist_ok=True)
   os.makedirs(backup_dir, exist_ok=True)
   
   # Initialize empty files if they don't exist
   for file_path in [clients_file, billing_file]:
       if not os.path.exists(file_path):
           with open(file_path, 'w', encoding='utf-8') as file:
               json.dump({file_path.split("_")[-1].split(".")[0]: []}, file)
   
   while True:
       print("\n===== DOCUMENT MANAGEMENT SYSTEM =====")
       print("1. Client Management")
       print("2. Case Documents")
       print("3. Billing & Invoices")
       print("4. Backup System")
       print("5. Exit")
       
       choice = input("\nEnter your choice (1-5): ")
       
       try:
           if choice == '1':
               # Client Management submenu
               print("\n--- CLIENT MANAGEMENT ---")
               print("1. View All Clients")
               print("2. Add New Client")
               print("3. Search Clients")
               print("4. Return to Main Menu")
               
               subchoice = input("\nEnter your choice (1-4): ")
               
               if subchoice == '1':
                   # View all clients
                   clients = load_clients(clients_file)
                   if clients:
                       print("\nCLIENT LIST:")
                       for client_id, info in clients.items():
                           print(f"ID: {client_id}, Name: {info['name']}, Contact: {info['contact']}")
                   else:
                       print("No clients found.")
               
               elif subchoice == '2':
                   # Add new client
                   client_id = input("Enter client ID (CLXXX format): ")
                   name = input("Enter client name: ")
                   contact = input("Enter client contact: ")
                   
                   if add_client(clients_file, client_id, name, contact):
                       print(f"Client {client_id} added successfully.")
               
               elif subchoice == '3':
                   # Search clients
                   search_term = input("Enter search term: ")
                   results = search_clients(clients_file, search_term)
                   
                   if results:
                       print(f"\nFound {len(results)} matching clients:")
                       for client in results:
                           print(f"ID: {client['id']}, Name: {client['name']}")
                   else:
                       print("No matching clients found.")
           
           elif choice == '2':
               # Case Documents submenu
               print("\n--- CASE DOCUMENTS ---")
               print("1. Create New Case")
               print("2. Create Case Document")
               print("3. View Case Document")
               print("4. Return to Main Menu")
               
               subchoice = input("\nEnter your choice (1-4): ")
               
               if subchoice == '1':
                   # Create new case
                   case_id = input("Enter case ID (CAXXX format): ")
                   case_dir = create_case_directory(cases_dir, case_id)
                   print(f"Case directory created: {case_dir}")
               
               elif subchoice == '2':
                   # Create case document
                   case_id = input("Enter case ID: ")
                   title = input("Enter document title: ")
                   date = input("Enter date (YYYY-MM-DD): ")
                   status = input("Enter status: ")
                   attorney = input("Enter attorney name: ")
                   
                   print("Enter document content (press Enter twice to finish):")
                   content_lines = []
                   while True:
                       line = input()
                       if not line and content_lines and not content_lines[-1]:
                           content_lines.pop()
                           break
                       content_lines.append(line)
                   
                   content = '\n'.join(content_lines)
                   
                   # Create document filename and path
                   doc_dir = os.path.join(cases_dir, case_id, 'documents')
                   if not os.path.exists(doc_dir):
                       os.makedirs(doc_dir)
                       
                   doc_filename = f"{case_id}_{title.replace(' ', '_')}.txt"
                   doc_path = os.path.join(doc_dir, doc_filename)
                   
                   # Create the document
                   create_case_document(doc_path, title, date, status, attorney, content)
                   print(f"Document created: {doc_path}")
               
               elif subchoice == '3':
                   # View case document
                   case_id = input("Enter case ID: ")
                   case_dir = os.path.join(cases_dir, case_id)
                   
                   if not os.path.exists(case_dir):
                       print(f"Case directory not found: {case_dir}")
                       continue
                   
                   # List documents in case directory
                   files = list_case_files(case_dir, '.txt')
                   
                   if not files:
                       print("No documents found for this case.")
                       continue
                   
                   print("\nAvailable documents:")
                   for i, file_info in enumerate(files, 1):
                       print(f"{i}. {file_info['name']}")
                   
                   file_num = int(input("\nEnter document number to view: "))
                   if 1 <= file_num <= len(files):
                       doc_path = files[file_num - 1]['full_path']
                       
                       # Display document
                       doc_data = read_case_document(doc_path)
                       
                       print("\n--- DOCUMENT METADATA ---")
                       for key, value in doc_data['metadata'].items():
                           print(f"{key}: {value}")
                       
                       print("\n--- DOCUMENT CONTENT ---")
                       print(doc_data['content'])
                   else:
                       print("Invalid document number.")
           
           elif choice == '3':
               # Billing & Invoices submenu
               print("\n--- BILLING & INVOICES ---")
               print("1. Record Billing Entry")
               print("2. Generate Invoice")
               print("3. Return to Main Menu")
               
               subchoice = input("\nEnter your choice (1-3): ")
               
               if subchoice == '1':
                   # Record billing entry
                   case_id = input("Enter case ID: ")
                   date = input("Enter date (YYYY-MM-DD): ")
                   hours = input("Enter hours worked: ")
                   rate = input("Enter hourly rate: ")
                   description = input("Enter description: ")
                   
                   record_billing(billing_file, case_id, date, hours, rate, description)
                   print("Billing entry recorded successfully.")
               
               elif subchoice == '2':
                   # Generate invoice
                   case_id = input("Enter case ID: ")
                   output_file = os.path.join(cases_dir, case_id, f"invoice_{case_id}_{datetime.datetime.now().strftime('%Y%m%d')}.txt")
                   
                   generate_invoice(billing_file, clients_file, case_id, output_file)
                   print(f"Invoice generated: {output_file}")
           
           elif choice == '4':
               # Backup system
               print("\nCreating backup...")
               count = backup_files(base_dir, backup_dir)
               print(f"Backup completed. {count} files backed up to {backup_dir}")
           
           elif choice == '5':
               # Exit
               print("Thank you for using the Document Management System")
               break
           
           else:
               print("Invalid choice. Please enter a number between 1 and 5.")
       
       except Exception as e:
           print(f"Error: {e}")


if __name__ == "__main__":
   main()