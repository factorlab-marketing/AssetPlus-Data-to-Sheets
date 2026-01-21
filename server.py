
from flask import Flask, request, jsonify, render_template
from google_sheets_manager import GoogleSheetManager
import os

app = Flask(__name__)

# Configuration
KEY_FILE = "service_account.json"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1OYSbV2V6qKCXm5YN1RE7PlDxOaRa_gSIOQ2_VUL4Lr4/edit?gid=603840523#gid=603840523"

def parse_block(text_block):
    """
    Parses a text block to extract key-value pairs.
    """
    if not text_block:
        return {}
        
    data = {}
    lines = [line.strip() for line in text_block.split('\n') if line.strip()]
    
    known_keys = [
        "Cash Input", "Investment", "Investments", "Gains", "Total", "Absolute", "XIRR", 
        "Name", "Email"
    ]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for "Key: Value"
        if ":" in line:
            parts = line.split(":", 1)
            key = parts[0].strip()
            val = parts[1].strip()
            data[key] = val
            i += 1
            continue
            
        # Check for Key \n Value
        is_key = False
        for k in known_keys:
            if k.lower() == line.lower():
                is_key = True
                if i + 1 < len(lines):
                    data[k] = lines[i+1] # Take next line as value
                    i += 2 
                else:
                    i += 1
                break
        
        if not is_key:
            i += 1
            
    return data

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.json
        user_name = data.get('userName')
        client_name = data.get('clientName')
        client_email = data.get('clientEmail')
        inside_text = data.get('insideText')
        outside_text = data.get('outsideText')
        
        if not user_name or not client_name or not client_email:
            return jsonify({'success': False, 'message': 'Missing required fields'})

        # Parse Inside
        inside_data = parse_block(inside_text)
        inside_data["Name"] = client_name
        inside_data["Email"] = client_email
        
        # Parse Outside
        outside_data = {}
        if outside_text and outside_text.strip():
            outside_data = parse_block(outside_text)
            outside_data["Name"] = client_name
            outside_data["Email"] = client_email
            
        # Add to Sheets
        manager = GoogleSheetManager(KEY_FILE, SHEET_URL)
        if manager.connect():
            success = manager.add_client_data(inside_data, outside_data, user_name)
            if success:
                return jsonify({'success': True, 'message': f'Successfully added {client_name}'})
            else:
                return jsonify({'success': False, 'message': 'Failed to add data to Sheet'})
        else:
            return jsonify({'success': False, 'message': 'Could not connect to Google Sheets'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("Starting Flask Server...")
    app.run(port=5000, debug=True)
