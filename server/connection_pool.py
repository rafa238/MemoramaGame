import threading
import socket
from typing import List, Optional, Tuple, Any

from game.event import GameEvent
from game.game_logic import GameLogic
from server.pool_state import PoolState


class ConnectionPool:
    def __init__(self, game_logic: GameLogic, max_connections=10) -> None:
        self.game_logic = game_logic
        self.max_connections: int = max_connections
        self.connections: List[Tuple[socket.socket, Any]] = []
        self.lock: threading.Lock = threading.Lock()
        self.state: PoolState = PoolState.STOPPED
        self.server_socket: Optional[socket.socket] = None

        game_logic.add_update_callback(self.broadcast)

    def start_pool(self, host: str = '127.0.0.1', port: int = 65432) -> None:
        if self.state in {PoolState.STARTING, PoolState.RUNNING}:
            print("El server ya está en ejecución o iniciándose.")
            return

        self.state = PoolState.STARTING
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((host, port))
            self.server_socket.listen(self.max_connections)
            self.state = PoolState.RUNNING
            print(f"Pool iniciado en {host}:{port}")
            threading.Thread(target=self.accept_connections).start()
        except Exception as e:
            print(f"Fallo al iniciar el server: {e}")
            self.state = PoolState.FAILED

    def accept_connections(self) -> None:
        try:
            while self.state == PoolState.RUNNING:
                conn, address = self.server_socket.accept()
                if not self.add_connection(conn, address):
                    conn.close()
                else:
                    self.game_logic.process_action(GameEvent.NEW_PLAYER, conn)
        except Exception as e:
            print(f"Error aceptando conexiones: {e}")
            self.state = PoolState.FAILED

    def add_connection(self, conn: socket.socket, address: str) -> bool:
        with self.lock:
            if self.state != PoolState.RUNNING or len(self.connections) >= self.max_connections:
                print("Conexión rechazada.")
                return False
            self.connections.append((conn, address))
            threading.Thread(target=self.listen_connection, args=(conn, address)).start()
            print(f"Cliente conectado desde {address}")
            return True

    def listen_connection(self, conn: socket.socket, address: str) -> None:
        try:
            cur_thread = threading.current_thread()
            print(f"Recibiendo datos del cliente {address} en el {cur_thread.name}")
            while True:
                data = conn.recv(1024)
                self.game_logic.process_action(GameEvent.MSG_RECEIVED_PLAYER, conn, data)
                if not data:
                    print(f"Cliente se desconecto {address}")
                    break
        except Exception as e:
            print(f"Error escuchando al cliente {address}: {e}")
        finally:
            print("Removiendo cliente...")
            self.remove_connection(conn)

    def remove_connection(self, conn: socket.socket) -> None:
        with self.lock:
            try:
                self.connections = [c for c in self.connections if c[0] != conn]
                conn.close()
            except Exception as e:
                print(f"Error al remover la conexion: {e}")

        self.game_logic.process_action(GameEvent.DISCONNECTED_PLAYER, conn)

    def broadcast(self, event: GameEvent, message: str) -> None:
        if self.state != PoolState.RUNNING:
            print("No se puede enviar mensaje, el server no está en ejecución.")
            return
        with self.lock:
            for conn, _ in self.connections:
                try:
                    conn.sendall(message.encode())
                except:
                    print(f"Error con el cliente")
                    self.remove_connection(conn)

    def stop_pool(self) -> None:
        if self.state != PoolState.RUNNING:
            print("El server no está en ejecución.")
            return
        self.state = PoolState.STOPPING
        with self.lock:
            for conn, _ in self.connections:
                conn.close()
            self.connections = []
        self.state = PoolState.STOPPED
        print("Pool detenido.")

    def failed_state(self) -> None:
        self.state = PoolState.FAILED
        print("El server ha fallado.")
