from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from flask_cors import CORS
import requests
from datetime import datetime

# Load environment variables from .env file
load_dotenv(r"B:\Winter Semester\AI DA\apikey.env")

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

# Store conversation context
conversation_history = {}

def fetch_stock_data(symbol):
    try:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={ALPHA_VANTAGE_API_KEY}'
        r = requests.get(url)
        data = r.json()

        time_series = data.get("Time Series (5min)", {})
        if not time_series:
            return None, "No data found for the provided symbol."

        table_data = []
        for timestamp, values in time_series.items():
            table_data.append({
                "Timestamp": timestamp,
                "Open": float(values["1. open"]),
                "High": float(values["2. high"]),
                "Low": float(values["3. low"]),
                "Close": float(values["4. close"]),
                "Volume": int(values["5. volume"])
            })

        table_data.sort(key=lambda x: x["Timestamp"], reverse=True)
        return table_data, None
    except Exception as e:
        return None, str(e)

def format_table_as_html(data):
    if not data:
        return ""
    
    html_table = """
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">
        <thead>
            <tr>
                <th>Timestamp</th>
                <th>Open</th>
                <th>High</th>
                <th>Low</th>
                <th>Close</th>
                <th>Volume</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for row in data[:5]:  # Show only last 5 entries for brevity
        html_table += f"""
            <tr>
                <td>{row['Timestamp']}</td>
                <td>{row['Open']:.2f}</td>
                <td>{row['High']:.2f}</td>
                <td>{row['Low']:.2f}</td>
                <td>{row['Close']:.2f}</td>
                <td>{row['Volume']:,}</td>
            </tr>
        """
    
    html_table += "</tbody></table>"
    return html_table

def extract_stock_info(text):
    """Helper function to extract stock information from GPT-4 response"""
    lines = text.strip().split('\n')
    result = {
        "is_financial": False,
        "response_type": "text",
        "symbols": [],
        "comparison_required": False,
        "message": ""
    }
    
    message_lines = []
    parsing_metadata = False
    
    for line in lines:
        line = line.strip()
        if line.startswith("METADATA:"):
            parsing_metadata = True
            continue
            
        if parsing_metadata:
            if line.startswith("IS_FINANCIAL:"):
                result["is_financial"] = line.split(":")[1].strip().lower() == "true"
            elif line.startswith("RESPONSE_TYPE:"):
                result["response_type"] = line.split(":")[1].strip().lower()
            elif line.startswith("SYMBOLS:"):
                symbols = line.split(":")[1].strip()
                result["symbols"] = [s.strip() for s in symbols.strip("[]").split(",") if s.strip()]
            elif line.startswith("COMPARISON:"):
                result["comparison_required"] = line.split(":")[1].strip().lower() == "true"
        else:
            message_lines.append(line)
            
    result["message"] = "\n".join(message_lines).strip()
    return result

def process_financial_query(user_message, session_id):
    conversation = conversation_history.get(session_id, [])
    
    # Prepare the conversation context for GPT
    messages = [
        {"role": "system", "content": """You are a Onboarding helper agent, Named Sam for new employee.
Format your response with a natural message first, and ask the user to enter his name, age company name and the role he is hass been selected for and then give him some onboarding instruction and answer for as that companies Hr manager helping the user."""}
    ]
    
    # Add conversation history
    for msg in conversation[-3:]:  # Include last 3 messages for context
        messages.append({"role": "user", "content": msg["user"]})
        if "assistant" in msg:
            messages.append({"role": "assistant", "content": msg["assistant"]})
    
    # Add current message
    messages.append({"role": "user", "content": user_message})
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",  # Using GPT-4
            messages=messages,
            temperature=0.0
        )
        
        return extract_stock_info(response.choices[0].message.content)
    except Exception as e:
        return {
            "is_financial": False,
            "response_type": "error",
            "symbols": [],
            "comparison_required": False,
            "message": str(e)
        }

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if not user_message:
        return jsonify({"response": "Please send a message."})

    try:
        # Initialize or get conversation history
        if session_id not in conversation_history:
            conversation_history[session_id] = []
            
        # Process the query
        result = process_financial_query(user_message, session_id)
        
        # Handle non-financial queries
        if not result["is_financial"]:
            response = result["message"]
            conversation_history[session_id].append({
                "user": user_message,
                "assistant": response
            })
            return jsonify({"response": response})
            
        # Handle financial queries
        if result["response_type"] == "data":
            all_data = {}
            for symbol in result["symbols"]:
                table_data, error = fetch_stock_data(symbol)
                if error:
                    return jsonify({"response": f"Error fetching data for {symbol}: {error}"})
                all_data[symbol] = table_data
            
            # Handle comparison if required
            if result["comparison_required"] and len(result["symbols"]) > 1:
                compare_message = f"\nComparison of latest prices:\n"
                for symbol in result["symbols"]:
                    latest_price = all_data[symbol][0]["Close"]
                    compare_message += f"{symbol}: ${latest_price:.2f}\n"
                
                response = compare_message + "\nDetailed data:\n"
                for symbol in result["symbols"]:
                    response += f"\n{symbol} Data:\n{format_table_as_html(all_data[symbol])}"
            else:
                symbol = result["symbols"][0]
                response = f"{result['message']}\n{format_table_as_html(all_data[symbol])}"
                
        else:
            response = result["message"]
            
        # Update conversation history
        conversation_history[session_id].append({
            "user": user_message,
            "assistant": response,
            "context": {
                "symbols": result["symbols"],
                "data_type": "stock_price"
            }
        })
        
        # Cleanup old conversations (keep only last 10 messages)
        if len(conversation_history[session_id]) > 10:
            conversation_history[session_id] = conversation_history[session_id][-10:]
            
        return jsonify({"response": response})

    except Exception as e:
        return jsonify({"response": f"An error occurred: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)