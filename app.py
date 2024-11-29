import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, session
from flask_session import Session
import openai
from dotenv import load_dotenv
from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Load environment variables from .env
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

app.config["SESSION_TYPE"] = "filesystem"
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", str(uuid.uuid4()))
Session(app)


# Get OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key is present
if not openai_api_key:
    raise ValueError("OpenAI API key is missing. Please set the OPENAI_API_KEY environment variable.")


openai.api_key = openai_api_key


# Initialize LangChain components
llm = OpenAI(temperature=0.7, api_key=openai_api_key)
memory = ConversationBufferMemory()
conversation = ConversationChain(llm=llm, memory=memory)



# Serve static files (HTML, CSS, JS)
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/<path:path>')
def static_file(path):
    return send_from_directory('static', path)


# Define a route for chatting
@app.route('/chat', methods=['POST'])
def chat():
    try:

        
        if 'conversation_history' not in session:
            session['conversation_history'] = [
                {"role": "system", "content": """ 
                You are Sophia, a virtual assistant for Nutra Company, a leader in health supplements and natural remedies. 
                You are 36 years old, a mother of two kids, and consider yourself a caring, supportive friend. 
                As an expert in nutrition, skincare, and nutrients, you are dedicated to helping customers improve their health 
                and general well-being in a compassionate and approachable manner, with a touch of humor when suitable. 
                """}
            ]

        # Get user message from the request
        user_message = request.json.get('message')
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400

        # Append user's message to conversation history
        session['conversation_history'].append({"role": "user", "content": user_message})

        # Call OpenAI API to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=session['conversation_history']
        )

        # Extract assistant's reply
        assistant_reply = response['choices'][0]['message']['content']

        # Append assistant's reply to conversation history
        session['conversation_history'].append({"role": "assistant", "content": assistant_reply})

        # Return the assistant's reply to the frontend
        return jsonify({'reply': assistant_reply})

    except Exception as e:
        # Add more detailed logging
        print(f"Error occurred: {str(e)}")
        #traceback.print_exc()
        return jsonify({'error': 'An error occurred while processing your request.'}), 500


# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)
