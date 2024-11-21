# OnBoarding-ChatBot


## Onboarding Chatbot

This project is a Flask-based web application designed to serve as an interactive chatbot that can:
1. Fetch and display stock market data using the Alpha Vantage API.
2. Handle general conversational queries, including onboarding assistance for new employees, powered by OpenAI's GPT model.

---

## Features

- **Conversational AI**:
  - Answers general queries.
  - Handles onboarding instructions for new employees in a simulated HR assistant role.

- **Session-Based Conversation**:
  - Maintains conversational context for multiple sessions.

- **REST API**:
  - POST endpoint for sending user queries and receiving chatbot responses.

---

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```

2. **Install Dependencies**:
   Make sure you have Python 3.7+ installed, then install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Environment Variables**:
   Create a `.env` file to store your API keys:
   ```env
   OPENAI_API_KEY=your_openai_api_key
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   ```

4. **Run the Application**:
   ```bash
   python app.py
   ```

5. **Access the Application**:
   The application will be available at `http://127.0.0.1:5000`.

---

## API Endpoints

### `/chat` (POST)
**Description**: Handles user queries, processes them via OpenAI's GPT or Alpha Vantage API, and returns responses.

- **Request Format**:
  ```json
  {
    "message": "Your query text",
    "session_id": "unique_session_identifier"
  }
  ```

- **Response Format**:
  ```json
  {
    "response": "Bot's response to the query"
  }
  ```

---

## File Structure

- **app.py**: Main application file.
- **requirements.txt**: List of Python dependencies.
- **.env**: (Not included) File for storing sensitive API keys.
- **templates**: Directory for HTML templates (if extended to a web-based UI).
- **static**: Directory for static assets like CSS/JS (optional).

---

## Key Functionalities

1. **Stock Data Fetching**:
   - Fetches and sorts stock data by timestamp.
   - Displays the top 5 recent records in an HTML table.

2. **GPT-4 Integration**:
   - Processes user input and generates responses.
   - Includes metadata for parsing financial queries.

3. **Session Management**:
   - Maintains up to the last 10 messages per session.

4. **Onboarding Assistance**:
   - Welcomes new employees.
   - Provides instructions and answers FAQs as an HR manager.

---

## Tech Stack

- **Backend**: Flask
- **API Integration**: OpenAI GPT, Alpha Vantage
- **Session Management**: Python dictionary
- **Environment Variables**: Python `dotenv`

---

## Future Improvements

- Add front-end for a better user experience.
- Improve error handling and user guidance.
- Extend chatbot capabilities for additional query types.

---

## Contributing

Feel free to fork the repository and submit pull requests for improvements or new features. Ensure all code changes are properly documented and tested.

---

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

---

**Author**: Abhinav Singh  
**Date**: November 2024
