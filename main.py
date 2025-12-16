# from dotenv import load_dotenv
import time
import socket
import json
import traceback
# import random
from concurrent import futures
from src.routes import MODELOS_ROUTES
HOST = '127.0.0.1' 
PORT = 65432  



def tcpServer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0)  # permite interrumpir accept()

        print(f"Servidor TCP escuchando en {HOST}:{PORT}")

        try:
            while True:
                try:
                    conn, addr = s.accept()
                    print("Conectado por:", addr)
                    conn.settimeout(1.0)  # permite interrumpir recv()
                except socket.timeout:
                    continue

                with conn:
                    while True:
                        try:
                            data = conn.recv(4096)
                            if not data:
                                print(f"🔌 Cliente desconectado: {addr}")
                                break


                            data_str = data.decode().strip()
                            # print(f"📥 Mensaje recibido: {repr(data_str)}")
                            # 💥 RESPONDER AL PING
                            if data_str == "PING":
                                conn.sendall(b"PONG\n")
                                continue

                            data_obj = json.loads(data_str)
                            action = data_obj.get("action")
                            if not action:
                                raise ValueError("Campo 'action' faltante")

                            if action in MODELOS_ROUTES:
                                print("action", action)
                                response = MODELOS_ROUTES[action](data_obj)
                                response_str = json.dumps(response)
                                conn.sendall(response_str.encode())
                            else:
                                error_msg = {
                                    "status": 700,
                                    "message": f"Acción desconocida: {action}",
                                    "data": {}
                                }
                                conn.sendall(json.dumps(error_msg).encode())

                        except socket.timeout:
                            continue  # da oportunidad a KeyboardInterrupt de ser lanzado

                        except json.JSONDecodeError as e:
                            error_msg = {
                                "status": 400,
                                "message": "JSON inválido",
                                "details": str(e)
                            }
                            conn.sendall(json.dumps(error_msg).encode())

                        except Exception as e:
                            error_msg = {
                                "status": 500,
                                "message": "Error interno del servidor",
                                "details": str(e),
                                "trace": traceback.format_exc()
                            }
                            print(f"❌ Error en handler: {e}")
                            print(traceback.format_exc())

                            if isinstance(e, ConnectionResetError):
                                print(f"🔌 Conexión reseteada por el cliente: {e}")
                                break  # cortá el loop y soltá el socket
                            else:
                                try:
                                    conn.sendall(json.dumps(error_msg).encode())
                                except:
                                    print("❌ Error al enviar mensaje de error:", traceback.format_exc())
                                    break

        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido manualmente con Ctrl+C")


if __name__ == '__main__':
    # load_dotenv()
    # serve()
    tcpServer()