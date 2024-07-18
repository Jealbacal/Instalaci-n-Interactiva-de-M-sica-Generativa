from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

# Define la función de manejo de mensajes OSC
def handler(address, *args):
    print(f"Mensaje recibido en la dirección '{address}': {args}")

# Crea un despachador y registra la función de manejo de mensajes
dispatcher = Dispatcher()

dispatcher.map("/mediapipe/handsR", handler)  # Mapea todos los mensajes OSC a esta función
# dispatcher.map("/mediapipe/hands/gest", handler)  # Mapea todos los mensajes OSC a esta función
# dispatcher.map("/mediapipe/hands/hand", handler)  # Mapea todos los mensajes OSC a esta función
# dispatcher.map("/mediapipe/hands/pos", handler)  # Mapea todos los mensajes OSC a esta función
# dispatcher.map("/mediapipe/hands/num_gest", handler)  # Mapea todos los mensajes OSC a esta función
dispatcher.map("/mediapipe/posR", handler) 
dispatcher.map("/mediapipe/handsL", handler)
dispatcher.map("/mediapipe/posL", handler)  
# Configura el servidor OSC para escuchar en el puerto 8080
server = BlockingOSCUDPServer(("127.0.0.1", 7500), dispatcher)

# Inicia el servidor y espera mensajes
print("Servidor OSC iniciado. Esperando mensajes...")
server.serve_forever()
