from flask import Flask, render_template, request, jsonify
import random
import os
import google.generativeai as genai
import traceback  # Added for better error tracking

app = Flask(__name__)

# Gemini API configuration
GEMINI_API_KEY = "AIzaSyDlmKmQxLl-urDBUCdl8nX29SPB0EbuxYw"  # Replace with your actual API key
genai.configure(api_key=GEMINI_API_KEY)

# Sample DIY home improvement responses
diy_responses = {
    "painting": [
        "For painting walls, start by cleaning the surface and applying painter's tape to edges.",
        "Use a primer before applying paint for better coverage and durability.",
        "When painting, work from top to bottom and maintain a wet edge to avoid lap marks."
    ],
    "plumbing": [
        "Always turn off the water supply before starting any plumbing work.",
        "Use plumber's tape on threaded connections to prevent leaks.",
        "Keep a bucket handy when disconnecting pipes to catch residual water."
    ],
    "flooring": [
        "Acclimate wood flooring in your home for at least 72 hours before installation.",
        "Start laying tiles from the center of the room and work outward for the best appearance.",
        "Use spacers between tiles to ensure even grout lines."
    ],
    "electrical": [
        "Always turn off power at the breaker before working on electrical projects.",
        "Use a voltage tester to confirm power is off before touching any wires.",
        "Follow local electrical codes when installing new fixtures or outlets."
    ],
    "default": [
        "What DIY project are you working on? I can help with painting, plumbing, flooring, or electrical work.",
        "Try asking about specific home improvement tasks like wall painting or fixing a leaky faucet.",
        "I can provide step-by-step instructions for many home improvement projects. What are you interested in?"
    ]
}

def is_diy_related(query):
    """Check if the query is related to DIY home improvement."""
    # Commenting out the constraint check - will always return True
    # diy_keywords = [
    #     'paint', 'plumb', 'pipe', 'leak', 'faucet', 'floor', 'tile', 'wood',
    #     'electric', 'wire', 'outlet', 'light', 'wall', 'ceiling', 'roof',
    #     'door', 'window', 'cabinet', 'kitchen', 'bathroom', 'repair', 'fix',
    #     'install', 'build', 'renovate', 'remodel', 'diy', 'home improvement',
    #     'tool', 'drill', 'saw', 'hammer', 'nail', 'screw', 'measure'
    # ]
    
    # return any(keyword in query.lower() for keyword in diy_keywords)
    return True  # Always return True to bypass the constraint

def get_gemini_response(prompt):
    """Get response from Gemini API using the official client library."""
    try:
        print(f"Sending to Gemini: {prompt}")  # Debug log
        
        # Add DIY context to the prompt but make it less restrictive
        diy_context = "You are a helpful assistant with expertise in DIY home improvement. While you specialize in home improvement topics, you can also answer other questions."
        
        full_prompt = f"{diy_context}\n\nUser question: {prompt}"
        
        # Create a model instance
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Generate content
        response = model.generate_content(full_prompt)
        
        # Return the text response
        print(f"Received from Gemini: {response.text[:100]}...")  # Debug log (first 100 chars)
        return response.text
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        return f"Sorry, I couldn't process your request at the moment. Error: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message', '')
    print(f"Received message: {user_message}")  # Debug log
    
    # Check if the query is DIY-related - constraint disabled
    # if not is_diy_related(user_message):
    #     print("Message not DIY-related")  # Debug log
    #     return jsonify({
    #         'response': "I'm your DIY Home Improvement assistant. Please ask me questions related to home improvement projects, repairs, or renovations."
    #     })
    
    # Try to get a response from Gemini API
    try:
        print("Calling Gemini API...")  # Debug log
        response = get_gemini_response(user_message)
        print("Successfully got response from Gemini")  # Debug log
        return jsonify({'response': response})
    except Exception as e:
        print(f"Error in get_response route: {str(e)}")
        print(traceback.format_exc())  # Print full traceback
        
        # Fall back to our basic response system if Gemini fails
        print("Falling back to basic responses")  # Debug log
        if 'paint' in user_message.lower():
            response = random.choice(diy_responses['painting'])
        elif any(word in user_message.lower() for word in ['plumb', 'pipe', 'leak', 'faucet']):
            response = random.choice(diy_responses['plumbing'])
        elif any(word in user_message.lower() for word in ['floor', 'tile', 'wood']):
            response = random.choice(diy_responses['flooring'])
        elif any(word in user_message.lower() for word in ['electric', 'wire', 'outlet', 'light']):
            response = random.choice(diy_responses['electrical'])
        else:
            response = random.choice(diy_responses['default'])
        
        return jsonify({'response': response})

if __name__ == '__main__':
    # Create templates directory and HTML file before running
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    with open('templates/index.html', 'w') as f:
        f.write('''
<!DOCTYPE html>
<html>
<head>
    <title>DIY Home Improvement Guide</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .chat-container {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            height: 300px;
            overflow-y: auto;
            margin-bottom: 10px;
        }
        .user-message {
            background-color: #e6f7ff;
            padding: 8px;
            border-radius: 5px;
            margin: 5px 0;
        }
        .bot-message {
            background-color: #f0f0f0;
            padding: 8px;
            border-radius: 5px;
            margin: 5px 0;
        }
        #user-input {
            width: 80%;
            padding: 8px;
        }
        button {
            padding: 8px 15px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        h1 {
            color: #333;
        }
    </style>
</head>
<body>
    <h1>DIY Home Improvement Guide</h1>
    <div class="chat-container" id="chat-container">
        <div class="bot-message">Hello! I'm your DIY Home Improvement assistant. Ask me about painting, plumbing, flooring, or electrical projects!</div>
    </div>
    <div>
        <input type="text" id="user-input" placeholder="Ask about a DIY project...">
        <button onclick="sendMessage()">Send</button>
    </div>

    <script>
        function sendMessage() {
            const userInput = document.getElementById('user-input');
            const chatContainer = document.getElementById('chat-container');
            const message = userInput.value.trim();
            
            if (message === '') return;
            
            // Add user message to chat
            const userDiv = document.createElement('div');
            userDiv.className = 'user-message';
            userDiv.textContent = message;
            chatContainer.appendChild(userDiv);
            
            // Clear input
            userInput.value = '';
            
            // Add loading message
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'bot-message';
            loadingDiv.textContent = 'Thinking...';
            loadingDiv.id = 'loading-message';
            chatContainer.appendChild(loadingDiv);
            
            // Scroll to bottom
            chatContainer.scrollTop = chatContainer.scrollHeight;
            
            // Get bot response
            fetch('/get_response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading message
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) {
                    loadingMessage.remove();
                }
                
                // Add bot response to chat
                const botDiv = document.createElement('div');
                botDiv.className = 'bot-message';
                botDiv.textContent = data.response;
                chatContainer.appendChild(botDiv);
                
                // Scroll to bottom
                chatContainer.scrollTop = chatContainer.scrollHeight;
            })
            .catch(error => {
                // Remove loading message
                const loadingMessage = document.getElementById('loading-message');
                if (loadingMessage) {
                    loadingMessage.remove();
                }
                
                // Add error message
                const errorDiv = document.createElement('div');
                errorDiv.className = 'bot-message';
                errorDiv.textContent = 'Sorry, there was an error processing your request.';
                chatContainer.appendChild(errorDiv);
                
                // Scroll to bottom
                chatContainer.scrollTop = chatContainer.scrollHeight;
                
                console.error('Error:', error);
            });
        }
        
        // Allow Enter key to send message
        document.getElementById('user-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
        ''')
    
    print("Starting Flask server...")  # Debug log
    app.run(debug=True)
