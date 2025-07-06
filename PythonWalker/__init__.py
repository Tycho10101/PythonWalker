from . import world_pb2
import requests
from . import player as player_template
from websockets.sync.client import connect as ws_conn
    
def login_with_pass(email, password):
    player = player_template.player()
    r = requests.post("https://api.pixelwalker.net/api/collections/users/auth-with-password", json={'identity': email, 'password': password})
    data = r.json()
    player.token = data["token"]
    record = data["record"]
    player.username = record["username"]
    player.id = record["id"]
    return player

def connect(world_id, user, on_chat=None, on_init=None, on_join=None, on_leave=None, commands=None):
    version = requests.get("https://game.pixelwalker.net/listroomtypes").json()[0]
    headers = {"Authorization": f"Bearer {user.token}"}
    r = requests.get(f"https://api.pixelwalker.net/api/joinkey/{version}/{world_id}", headers=headers)
    join_key = r.json()["token"]
    player_list = {}
    
    with ws_conn(f"wss://game.pixelwalker.net/ws?joinKey={join_key}") as websocket:
        while True:
            message = websocket.recv()
            packet = world_pb2.WorldPacket()
            packet.ParseFromString(message)
            #print(f"Received: {packet}")
            
            if packet.HasField("player_init_packet"):
                send = world_pb2.WorldPacket(player_init_received=world_pb2.PlayerInitReceivedPacket()).SerializeToString()
                websocket.send(send)
                if commands:
                    for command in commands.keys():
                        cmd = world_pb2.PlayerChatPacket()
                        cmd.message = f"/custom register {command}"
                        send = world_pb2.WorldPacket(player_chat_packet=cmd).SerializeToString()
                        websocket.send(send)
                player_id = packet.player_init_packet.player_properties.player_id
                _run_user_handle(on_init, websocket, world_pb2, player_list, packet.player_init_packet)
                
            elif packet.HasField("player_chat_packet"):
                if not packet.player_chat_packet.player_id == player_id:
                    _run_user_handle(on_chat, websocket, world_pb2, player_list, packet.player_chat_packet)
                    
            elif packet.HasField("ping"):
                send = world_pb2.WorldPacket(ping=world_pb2.Ping()).SerializeToString()
                websocket.send(send)
                
            elif packet.HasField("player_joined_packet"):
                player_list[packet.player_joined_packet.properties.player_id] = packet.player_joined_packet.properties.username
                _run_user_handle(on_join, websocket, world_pb2, player_list, packet.player_joined_packet)
                
            elif packet.HasField("player_left_packet"):
                _run_user_handle(on_leave, websocket, world_pb2, player_list, packet.player_left_packet)
                del player_list[packet.player_left_packet.player_id]
            
            elif packet.HasField("player_direct_message_packet"):
                if commands:
                    for command in commands.keys():
                        if f"//{command}" == packet.player_direct_message_packet.message or f"{packet.player_direct_message_packet.message}".startswith(f"//{command} "):
                            _run_custom_cmd(commands[command], websocket, world_pb2, player_list, packet.player_direct_message_packet.from_player_id, packet.player_direct_message_packet.message)
            
class Connection:
    def __init__(self, websocket, world_pb2, player_list):
        self.websocket = websocket
        self.proto = world_pb2
        self.players = player_list
    
    def send_chat(self, message):
        packet = self.proto.PlayerChatPacket()
        packet.message = message
        send = self.proto.WorldPacket(player_chat_packet=packet).SerializeToString()
        self.websocket.send(send)
        
def _run_user_handle(function, websocket, world_pb2, player_list, packet):
    if function:
        function(Connection(websocket, world_pb2, player_list), packet)
        
def _run_custom_cmd(function, websocket, world_pb2, player_list, player_id, message):
    args = message.split(' ')[1:]
    function(Connection(websocket, world_pb2, player_list), args, player_id)