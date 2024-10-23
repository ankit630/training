from flask import Flask
app = Flask(__name__)

@app.route('/')
def payment_service():
    return '''
    <html>
        <head>
            <title>MicroStore - Payment Service</title>
            <style>
                body { font-family: Arial; margin: 40px; background: #f0f0ff; }
                .status { padding: 20px; background: white; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
                h1 { color: #2c3e50; }
            </style>
        </head>
        <body>
            <h1>💳 MicroStore Payment Service</h1>
            <div class="status">
                <h2>Status: Online</h2>
                <p>Port: 5004</p>
                <p>Service: Processes payments and transactions</p>
                <p>Access this service via: <span id="url"></span></p>
            </div>
            <script>
                document.getElementById('url').textContent = window.location.href;
            </script>
        </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)
