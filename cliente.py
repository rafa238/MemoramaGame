import socket
import threading
import time

HOST = "127.0.0.1"  # Dirección IP del servidor
PORT = 65432  # Puerto del servidor
buffer_size = 1024

# Inicializar la matriz founded_words como una lista de listas
founded_words = [["*" for _ in range(2)] for _ in range(2)]


def receive_messages(TCPClientSocket):
    while True:
        data = TCPClientSocket.recv(buffer_size)
        data = data.decode("utf-8")
        print("\nMensaje recibido:", data)
        words = data.split(" ")

        if words[0] == "FLIP":
            word = words[-1]
            x, y = words[-2].split(",")
            x, y = int(x), int(y)

            founded_words[x - 1][y - 1] = word[0]

            print("Matriz actualizada:")
            for row in founded_words:
                print(" ".join(row))

        if not data:
            print("Se cerró la conexión con el servidor.")
            break


if __name__ == "__main__":
    print("**INTRUCCIONES**")
    print("Para voltear una carta ejecuta la instruccion FLIP seguido de las coordenadas separadas por una coma")
    print("Ejemplo: FLIP 1,1")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as TCPClientSocket:
        TCPClientSocket.connect((HOST, PORT))

        # Inicia el hilo para recibir mensajes
        receive_thread = threading.Thread(target=receive_messages, args=(TCPClientSocket,))
        receive_thread.start()

        # Bucle principal para enviar mensajes al servidor
        while True:
            time.sleep(2)
            msg = input("Ingresa las coordenadas a chequear: ")
            TCPClientSocket.sendall(msg.encode())
