import requests
from urllib.parse import urlencode
import json
from pathlib import Path
import time
from dotenv import load_dotenv
import os


#    https://dip.bundestag.de/erweiterte-suche?f.wahlperiode=20&f.typ=Dokument&f.vorgangstyp_p=01Antr%C3%A4ge&f.urheber_p=05BT-Fraktionen%2FGruppen&f.urheber_p=05BT-Fraktionen%2FGruppen~Fraktion%20der%20AfD&f.datum.start=2023-01-01&f.datum.end=2023-12-31&rows=100
#   https://dip.bundestag.de/erweiterte-suche?f.wahlperiode=20&f.urheber_p=05BT-Fraktionen%2FGruppen&f.urheber_p=05BT-Fraktionen%2FGruppen~Fraktion%20der%20AfD&f.datum.start=2023-01-01&f.datum.end=2023-12-31&rows=100
# https://search.dip.bundestag.de/api/v1/aktivitaet?f.datum.start=2023-01-01&f.datum.end=2023-12-31&f.drucksachetyp=Antrag&f.urheber=Bundesregierung&f.vorgangstyp=Gesetzgebung&f.vorgangstyp_notation=100&format=json&apikey=I9FKdCn.hbfefNWCY336dL6x62vfwNKpoN2RZ1gp21
# Load environment variables from .env file
load_dotenv()

class BundestagAPIClient:
    def __init__(self, api_key):
        self.base_url = "https://search.dip.bundestag.de/api/v1"
        self.api_key = api_key
        self.headers = {
            "Authorization": f"ApiKey {api_key}",
            "Accept": "application/json"
        }

    def search_documents(self):
        """
        Search for documents using the provided parameters
        """
        api_params = {
            "f.wahlperiode": "20",
            "f.typ": "Dokument",
            "f.vorgangstyp": "01Anträge",
            "f.urheber": "Fraktion der AfD",  # Updated based on working example
            "f.datum.start": "2023-01-01",
            "f.datum.end": "2023-12-31",
            "format": "json",
            "apikey": self.api_key,  # Including API key in params as shown in working example
            "rows": 100
        }
        
        print(f"Making request to: {self.base_url}/vorgang")  # Changed to /vorgang
        response = requests.get(
            f"{self.base_url}/vorgang",  # Changed to /vorgang
            params=api_params
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error response content: {response.text}")
            response.raise_for_status()

    def download_pdf(self, document_id, output_dir):
        """
        Download a PDF for a specific document
        """
        # First get the document details
        params = {"format": "json", "apikey": self.api_key}
        response = requests.get(
            f"{self.base_url}/vorgang/{document_id}",
            params=params
        )
        
        if response.status_code == 200:
            doc_data = response.json()
            print(f"Document data structure: {json.dumps(doc_data, indent=2)}")
            
            # We'll need to adjust this based on the actual response structure
            pdf_url = None
            if 'dokumentURL' in doc_data:
                pdf_url = doc_data['dokumentURL']
            
            if pdf_url:
                pdf_response = requests.get(pdf_url, params={"apikey": self.api_key})
                if pdf_response.status_code == 200:
                    output_path = Path(output_dir) / f"{document_id}.pdf"
                    output_path.write_bytes(pdf_response.content)
                    return str(output_path)
            else:
                print(f"No PDF URL found in document data")
        else:
            print(f"Failed to get document details: {response.status_code}")
        
        return None

def main():
    api_key = os.getenv("API_KEY")
    output_dir = Path("downloaded_pdfs")
    output_dir.mkdir(exist_ok=True)
    
    client = BundestagAPIClient(api_key)
    
    try:
        results = client.search_documents()
        
        if results:
            print(f"Found documents: {json.dumps(results, indent=2)}")
            
            documents = results.get("documents", [])
            print(f"Number of documents found: {len(documents)}")
            
            for doc in documents:
                doc_id = doc.get("id")
                if doc_id:
                    print(f"Downloading document {doc_id}...")
                    pdf_path = client.download_pdf(doc_id, output_dir)
                    if pdf_path:
                        print(f"Successfully downloaded to {pdf_path}")
                    else:
                        print(f"Failed to download document {doc_id}")
                    
                    time.sleep(1)
                
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    main()


