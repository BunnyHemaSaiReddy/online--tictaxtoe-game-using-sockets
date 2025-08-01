import socket
import threading
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 29845))  # Railway will assign a port

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
        try:
            self.players[0].sendall(b'X')
            self.players[1].sendall(b'O')
        except Exception as e:
            print(f"[ERROR] Failed to send symbols: {e}")
            return

        while True:
            try:
                current = self.players[self.turn]
                other = self.players[1 - self.turn]

                current.sendall(b"YOUR_MOVE")
                move_data = current.recv(1024)
                if not move_data:
                    break

                move = int(move_data.decode())

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
        if len(waiting_players) == 1:
            try:
                conn.sendall(b"WAITING_FOR_OPPONENT")
            except:
                waiting_players.remove(conn)
                return
        if len(waiting_players) >= 2:
            p1 = waiting_players.pop(0)
            p2 = waiting_players.pop(0)
            game = GameThread(p1, p2)
            game.start()
            games.append(game)

while True:
    conn, addr = server.accept()
    print(f"[CONNECTED] {addr}")
    threading.Thread(target=handle_new_connection, args=(conn,)).start()
