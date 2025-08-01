
import socket
import threading
import os

# Use '0.0.0.0' to accept connections from any IP
HOST = os.environ.get("HOST", "0.0.0.0")  # For deployment use env var or default to public
PORT = int(os.environ.get("PORT", 12345))  # Render sets $PORT automatically

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
print(f"[STARTED] Server running on {HOST}:{PORT}")

waiting_players = []
games = []
lock = threading.Lock()

class GameThread(threading.Thread):
    def __init__(self, player1, player2):
        threading.Thread.__init__(self)
        self.players = [player1, player2]
        self.board = [' '] * 9
        self.turn = 0

    def run(self):
        print("[GAME] New game started between 2 players.")
        self.players[0].sendall(b'X')
        self.players[1].sendall(b'O')
        while True:
            try:
                current = self.players[self.turn]
                other = self.players[1 - self.turn]
                current.sendall(b"YOUR_MOVE")
                move = int(current.recv(1024).decode())

                if self.board[move] == ' ':
                    self.board[move] = 'X' if self.turn == 0 else 'O'
                    for p in self.players:
                        p.sendall(f"MOVE {move} {self.board[move]}".encode())

                    if self.check_win():
                        current.sendall(b"WIN")
                        other.sendall(b"LOSE")
                        break
                    elif ' ' not in self.board:
                        for p in self.players:
                            p.sendall(b"DRAW")
                        break

                    self.turn = 1 - self.turn
                else:
                    current.sendall(b"INVALID")
            except Exception as e:
                print(f"[ERROR] {e}")
                break

        for p in self.players:
            try:
                p.close()
            except:
                pass
        print("[GAME] Game ended.")

    def check_win(self):
        b = self.board
        wins = [(0,1,2), (3,4,5), (6,7,8),
                (0,3,6), (1,4,7), (2,5,8),
                (0,4,8), (2,4,6)]
        for x, y, z in wins:
            if b[x] == b[y] == b[z] and b[x] != ' ':
                return True
        return False

def handle_new_connection(conn):
    with lock:
        waiting_players.append(conn)
        if len(waiting_players) >= 2:
            p1 = waiting_players.pop(0)
            p2 = waiting_players.pop(0)
            game = GameThread(p1, p2)
            game.start()
            games.append(game)

# Accept connections forever
while True:
    conn, addr = server.accept()
    print(f"[CONNECTED] {addr}")
    threading.Thread(target=handle_new_connection, args=(conn,)).start()
