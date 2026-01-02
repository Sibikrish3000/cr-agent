"""
Quick test script to upload and query the test_policy.txt document
"""
import requests
import os

# Configuration
API_BASE = "http://localhost:8000"
TEST_FILE = "uploads/test_policy.txt"

def test_document_query():
    """Test uploading and querying a document"""
    
    # Check if file exists
    if not os.path.exists(TEST_FILE):
        print(f"❌ File not found: {TEST_FILE}")
        return
    
    # Step 1: Upload the file
    print("📤 Step 1: Uploading test_policy.txt...")
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (os.path.basename(TEST_FILE), f, 'text/plain')}
        response = requests.post(f"{API_BASE}/upload", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    upload_result = response.json()
    print(f"✅ Upload successful!")
    print(f"   File path: {upload_result['file_path']}")
    print(f"   Document ID: {upload_result['document_id']}")
    
    file_path = upload_result['file_path']
    
    # Step 2: Query about remote work policy
    print("\n🤔 Step 2: Asking 'What is the remote work policy?'...")
    response = requests.post(
        f"{API_BASE}/chat",
        json={
            "query": "What is the remote work policy?",
            "file_path": file_path
        }
    )
    
    if response.status_code != 200:
        print(f"❌ Query failed: {response.text}")
        return
    
    result = response.json()
    print(f"\n✅ Response:\n{result['response']}")
    
    # Step 3: Query about specific details
    print("\n\n🤔 Step 3: Asking 'What equipment does the company provide?'...")
    response = requests.post(
        f"{API_BASE}/chat",
        json={
            "query": "What equipment does the company provide for remote work?",
            "file_path": file_path
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Response:\n{result['response']}")
    
    # Step 4: Query about work hours
    print("\n\n🤔 Step 4: Asking 'What are the core hours?'...")
    response = requests.post(
        f"{API_BASE}/chat",
        json={
            "query": "What are the core work hours for remote employees?",
            "file_path": file_path
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ Response:\n{result['response']}")

if __name__ == "__main__":
    print("=" * 60)
    print("DOCUMENT AGENT TEST - Remote Work Policy")
    print("=" * 60)
    test_document_query()
    print("\n" + "=" * 60)
    print("TEST COMPLETED!")
    print("=" * 60)
