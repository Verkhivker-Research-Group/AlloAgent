from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from biomni_biolab.agent import A1
import os

app = Flask(__name__)
CORS(app)
agent = A1(llm="gpt-4o", allosteric=True, api_key=os.environ["OPENAI_API_KEY"])

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/process', methods=['POST'])
def process_prompt():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Call your agent function
        log, final_output = agent.go(prompt)
        
        return jsonify({
            'success': True,
            'output': final_output
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5010")
    app.run(debug=True, port=5010, host='0.0.0.0')