import requests
import sys

def test_deployment(url):
    """
    Test if the deployment is working by making a request to the specified URL.
    
    Args:
        url (str): The URL of the deployed application
        
    Returns:
        bool: True if the deployment is working, False otherwise
    """
    try:
        print(f"Testing deployment at {url}...")
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Success! Server responded with status code {response.status_code}")
            print(f"Response content type: {response.headers.get('Content-Type', 'unknown')}")
            return True
        else:
            print(f"❌ Error: Server responded with status code {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: Could not connect to the server: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = input("Enter your PythonAnywhere URL (e.g., http://jugglegent.pythonanywhere.com): ")
    
    test_deployment(url)