from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from biomni_biolab.agent import A1
import os
import time
import threading
import json

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

@app.route('/process_stream', methods=['POST'])
def process_stream():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    def generate():
        # Reset log
        agent.log = []
        result = {'output': None}
        
        # Run agent in background thread
        def run_agent():
            log, final_output = agent.go(prompt)
            result['output'] = final_output
        
        thread = threading.Thread(target=run_agent)
        thread.start()
        
        # Stream log entries as they appear
        sent_count = 0
        while thread.is_alive() or sent_count < len(agent.log):
            # Send any new log entries
            while sent_count < len(agent.log):
                yield f"data: {json.dumps({'type': 'log', 'content': agent.log[sent_count]})}\n\n"
                sent_count += 1
            time.sleep(0.2)  # Check every 200ms
        
        # Send final output
        yield f"data: {json.dumps({'type': 'complete', 'output': result['output']})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:5010")
    app.run(debug=True, port=5010, host='0.0.0.0')