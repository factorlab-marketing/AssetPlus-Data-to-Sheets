
import gspread
import os
import json
from google.oauth2.service_account import Credentials


class GoogleSheetManager:
    def __init__(self, key_file_path, sheet_name):
        self.scope = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        self.key_file_path = key_file_path
        self.sheet_name = sheet_name
        self.client = None
        self.spreadsheet = None

    def connect(self):
        try:
            # Check for GOOGLE_CREDENTIALS_JSON env var first (Production/Vercel)
            config_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            if config_json:
                creds_dict = json.loads(config_json)
                creds = Credentials.from_service_account_info(creds_dict, scopes=self.scope)
            elif os.path.exists(self.key_file_path):
                # Fallback to local file
                creds = Credentials.from_service_account_file(self.key_file_path, scopes=self.scope)
            else:
                print("No credentials found (Env var or file).")
                return False

            self.client = gspread.authorize(creds)
            
            if self.sheet_name.startswith("http"):
                self.spreadsheet = self.client.open_by_url(self.sheet_name)
            else:
                self.spreadsheet = self.client.open(self.sheet_name)
                
            print(f"Connected to Google Sheet: {self.spreadsheet.title}")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def ensure_sheets_exist(self, sheet_names=["Inside", "Outside"]):
        """Ensures that the required worksheets exist."""
        if not self.spreadsheet:
            return
        
        existing_titles = [ws.title for ws in self.spreadsheet.worksheets()]
        
        for name in sheet_names:
            if name not in existing_titles:
                try:
                    self.spreadsheet.add_worksheet(title=name, rows=100, cols=20)
                    print(f"Created sheet: {name}")
                    # Add headers if creating new
                    if name == "Inside":
                        headers = ["Name", "Email", "Cash Input", "Investment", "Gains", "Total", "Absolute", "XIRR", "Added_By"]
                    else:
                        # Outside headers
                        headers = ["Name", "Email", "Investments", "Gains", "Total", "Absolute", "XIRR", "Added_By"]
                    
                    self.spreadsheet.worksheet(name).append_row(headers)
                    
                except Exception as e:
                    print(f"Error creating sheet {name}: {e}")

    def add_client_data(self, client_data_inside, client_data_outside, added_by):
        """
        Adds client data to both sheets.
        client_data_inside: dict corresponding to Inside headers
        client_data_outside: dict corresponding to Outside headers (can be empty)
        added_by: str name of the person adding the data
        """
        if not self.spreadsheet:
            print("Not connected to spreadsheet.")
            return False

        try:
            # Add to Inside
            ws_inside = self.spreadsheet.worksheet("Inside")
            row_inside = [
                client_data_inside.get("Name", ""),
                client_data_inside.get("Email", ""),
                client_data_inside.get("Cash Input", ""),
                client_data_inside.get("Investment", ""),
                client_data_inside.get("Gains", ""),
                client_data_inside.get("Total", ""),
                client_data_inside.get("Absolute", ""),
                client_data_inside.get("XIRR", ""),
                added_by
            ]
            ws_inside.append_row(row_inside)
            
            # Add to Outside
            ws_outside = self.spreadsheet.worksheet("Outside")
            
            if client_data_outside:
                row_outside = [
                    client_data_outside.get("Name", client_data_inside.get("Name", "")),
                    client_data_outside.get("Email", client_data_inside.get("Email", "")), 
                    client_data_outside.get("Investments", client_data_outside.get("Investment", "")),
                    client_data_outside.get("Gains", ""),
                    client_data_outside.get("Total", ""),
                    client_data_outside.get("Absolute", ""),
                    client_data_outside.get("XIRR", ""),
                    added_by
                ]
            else:
                row_outside = [
                    client_data_inside.get("Name", ""),
                    client_data_inside.get("Email", ""),
                    "-", "-", "-", "-", "-",
                    added_by
                ]
                
            ws_outside.append_row(row_outside)
            
            print(f"Successfully added data for {client_data_inside.get('Name')}")
            return True

        except Exception as e:
            print(f"Error adding data: {e}")
            return False

if __name__ == "__main__":
    # Example Usage
    # manager = GoogleSheetManager("path_to_key.json", "Sheet Name")
    # manager.connect()
    pass
