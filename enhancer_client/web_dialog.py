"""
Web-based dialog for accepting/rejecting enhanced prompts.
Opens in browser - much more reliable than tkinter!
"""
from flask import Flask, render_template_string, request, jsonify
import threading
import webbrowser
import queue
import time
from enhancer_client.enhancer.api_client import enhance_prompt_from_api, send_feedback_to_api
from enhancer_client.enhancer.config import settings
from enhancer_client.enhancer.state import set_last_session_id, set_last_prompts
import pyperclip
import uuid

# Queue for pending enhancements
pending_enhancements = queue.Queue()

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'promptboost-secret-key'

# HTML template for the dialog
DIALOG_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PromptBoost - Enhancement Ready</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px;
            text-align: center;
            color: white;
        }
        
        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 14px;
        }
        
        .content {
            padding: 30px;
        }
        
        .prompt-box {
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .info {
            background: #e7f5ff;
            border-left: 4px solid #339af0;
            padding: 15px;
            margin-bottom: 25px;
            border-radius: 8px;
            font-size: 14px;
            color: #1971c2;
        }
        
        .buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        
        .btn {
            padding: 15px 35px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        }
        
        .btn:active {
            transform: translateY(0);
        }
        
        .btn-accept {
            background: #51cf66;
            color: white;
        }
        
        .btn-reject {
            background: #ff6b6b;
            color: white;
        }
        
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #868e96;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✨ Prompt Enhanced!</h1>
            <p>Your prompt has been improved by AI</p>
        </div>
        
        <div class="content">
            <div class="prompt-box">{{ enhanced_text }}</div>
            
            <div class="info">
                💡 <strong>Choose an option:</strong> Accept to keep this enhancement, or Reject to get a different version.
            </div>
            
            <div class="buttons">
                <button class="btn btn-reject" onclick="handleReject()" id="rejectBtn">
                    🔄 Reject & Get Different
                </button>
                <button class="btn btn-accept" onclick="handleAccept()" id="acceptBtn">
                    ✅ Accept
                </button>
            </div>
            
            <div class="loading" id="loading" style="display: none;">
                <div class="spinner"></div>
                <p>Getting a different enhancement...</p>
            </div>
        </div>
    </div>
    
    <script>
        const sessionId = "{{ session_id }}";
        const originalPrompt = {{ original_prompt | tojson }};
        
        async function handleAccept() {
            document.getElementById('acceptBtn').disabled = true;
            document.getElementById('rejectBtn').disabled = true;
            
            try {
                const response = await fetch('/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        session_id: sessionId, 
                        action: 'accepted' 
                    })
                });
                
                if (response.ok) {
                    // Close the window after a short delay
                    setTimeout(() => window.close(), 500);
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to send feedback. Please try again.');
                document.getElementById('acceptBtn').disabled = false;
                document.getElementById('rejectBtn').disabled = false;
            }
        }
        
        async function handleReject() {
            document.getElementById('acceptBtn').disabled = true;
            document.getElementById('rejectBtn').disabled = true;
            document.getElementById('loading').style.display = 'block';
            document.querySelector('.buttons').style.display = 'none';
            
            try {
                const response = await fetch('/feedback', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        session_id: sessionId, 
                        action: 'rejected',
                        original_prompt: originalPrompt
                    })
                });
                
                if (response.ok) {
                    const data = await response.json();
                    if (data.redirect_url) {
                        // Redirect to new enhancement
                        window.location.href = data.redirect_url;
                    }
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to get different enhancement. Please try again.');
                document.getElementById('acceptBtn').disabled = false;
                document.getElementById('rejectBtn').disabled = false;
                document.getElementById('loading').style.display = 'none';
                document.querySelector('.buttons').style.display = 'flex';
            }
        }
        
        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') handleAccept();
            if (e.key === 'Escape') handleAccept(); // Treat ESC as accept
        });
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Home page - shows pending enhancement or waiting message."""
    try:
        enhancement_data = pending_enhancements.get_nowait()
        return render_template_string(
            DIALOG_HTML,
            enhanced_text=enhancement_data['enhanced_text'],
            session_id=enhancement_data['session_id'],
            original_prompt=enhancement_data['original_prompt']
        )
    except queue.Empty:
        return '<h1>No pending enhancements. Please wait...</h1>', 404

@app.route('/feedback', methods=['POST'])
def handle_feedback():
    """Handle Accept/Reject feedback."""
    data = request.json
    session_id = uuid.UUID(data['session_id'])
    action = data['action']
    
    print(f"💬 User {action} enhancement for session {session_id}")
    
    # Send feedback to API
    send_feedback_to_api(session_id, action)
    
    if action == 'rejected':
        # Get new enhancement
        original_prompt = data.get('original_prompt', '')
        user_id = settings.USER_ID
        new_session_id = uuid.uuid4()
        
        print("📤 Requesting different enhancement...")
        new_enhanced_text = enhance_prompt_from_api(
            prompt_text=original_prompt,
            user_id=user_id,
            session_id=new_session_id,
            is_reroll=True,
            original_prompt=original_prompt
        )
        
        if new_enhanced_text:
            set_last_session_id(new_session_id)
            set_last_prompts(original_prompt, new_enhanced_text)
            pyperclip.copy(new_enhanced_text)
            
            # Queue the new enhancement
            pending_enhancements.put({
                'enhanced_text': new_enhanced_text,
                'session_id': str(new_session_id),
                'original_prompt': original_prompt
            })
            
            return jsonify({'status': 'success', 'redirect_url': '/'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to get new enhancement'}), 500
    
    return jsonify({'status': 'success'})

def run_web_server():
    """Run the Flask server in a background thread."""
    app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)

def start_web_server():
    """Start the web server in a daemon thread."""
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start
    print("✅ Web dialog server started on http://127.0.0.1:5555")

def show_enhancement_in_browser(enhanced_text, session_id, original_prompt):
    """
    Queue an enhancement and open browser to show it.
    This is the replacement for the tkinter dialog.
    """
    pending_enhancements.put({
        'enhanced_text': enhanced_text,
        'session_id': str(session_id),
        'original_prompt': original_prompt
    })
    
    # Open browser automatically
    webbrowser.open('http://127.0.0.1:5555')
    print("🌐 Opening browser with enhanced prompt...")