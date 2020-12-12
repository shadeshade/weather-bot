from app import server
from app.credentials import SERVER_IP, PORT, DEBUG

run_app = server

if __name__ == '__main__':
    server.run(threaded=True, host=SERVER_IP, port=PORT, debug=DEBUG, use_reloader=False)
