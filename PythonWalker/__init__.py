from . import world_pb2
import requests
from . import player as player_template
from websockets.sync.client import connect as ws_conn
from . import world
    
def login_with_pass(email, password):
    print("Logging in...")
    player = player_template.player()
    r = requests.post("https://api.pixelwalker.net/api/collections/users/auth-with-password", json={'identity': email, 'password': password})
    data = r.json()
    player.token = data["token"]
    record = data["record"]
    player.username = record["username"]
    player.id = record["id"]
    print("Logged in")
    return player

def connect(world_id, user, on_chat=None, on_init=None, on_join=None, on_leave=None, on_block=None, commands=None, custom_init=False):
    print("Getting world type...")
    version = requests.get("https://server.pixelwalker.net/listroomtypes").json()[0]
    print("Getting join key...")
    headers = {"Authorization": f"Bearer {user.token}"}
    r = requests.get(f"https://api.pixelwalker.net/api/joinkey/{version}/{world_id}", headers=headers)
    join_key = r.json()["token"]
    player_list = {}
    print("Gathering block info...")
    block_list = requests.get('https://server.pixelwalker.net/listblocks').json()
    
    print("Connecting...")
    with ws_conn(f"wss://server.pixelwalker.net/ws?joinKey={join_key}", max_size=None) as websocket:
        print("Connected")
        while True:
            message = websocket.recv()
            packet = world_pb2.WorldPacket()
            packet.ParseFromString(message)
            #print(f"Received: {packet}")
            
            if packet.HasField("player_init_packet"):
                if not custom_init:
                    send = world_pb2.WorldPacket(player_init_received=world_pb2.PlayerInitReceivedPacket()).SerializeToString()
                    websocket.send(send)
                    
                world_data = world.decode(packet.player_init_packet.world_data, block_list, packet.player_init_packet.world_width, packet.player_init_packet.world_height)
                    
                if commands:
                    for command in commands.keys():
                        cmd = world_pb2.PlayerChatPacket()
                        cmd.message = f"/custom register {command}"
                        send = world_pb2.WorldPacket(player_chat_packet=cmd).SerializeToString()
                        websocket.send(send)
                player_id = packet.player_init_packet.player_properties.player_id
                _run_user_handle(on_init, websocket, world_pb2, player_list, packet.player_init_packet, world_data)
                
            elif packet.HasField("player_chat_packet"):
                if not packet.player_chat_packet.player_id == player_id:
                    _run_user_handle(on_chat, websocket, world_pb2, player_list, packet.player_chat_packet, world_data)
                    
            elif packet.HasField("ping"):
                send = world_pb2.WorldPacket(ping=world_pb2.Ping()).SerializeToString()
                websocket.send(send)
                
            elif packet.HasField("player_joined_packet"):
                player_list[packet.player_joined_packet.properties.player_id] = packet.player_joined_packet.properties.username
                _run_user_handle(on_join, websocket, world_pb2, player_list, packet.player_joined_packet, world_data)
                
            elif packet.HasField("player_left_packet"):
                _run_user_handle(on_leave, websocket, world_pb2, player_list, packet.player_left_packet, world_data)
                del player_list[packet.player_left_packet.player_id]
                
            elif packet.HasField('world_block_placed_packet'):
                id = packet.world_block_placed_packet.block_id
                if packet.world_block_placed_packet.layer == 0:
                    layer = 'bg'
                if packet.world_block_placed_packet.layer == 1:
                    layer = 'fg'
                if packet.world_block_placed_packet.layer == 2:
                    layer = 'ol'
                if packet.world_block_placed_packet.extra_fields:
                    block_data = world.decode_block_placed_data(packet.world_block_placed_packet.extra_fields)
                else:
                    block_data = []
                    
                for position in packet.world_block_placed_packet.positions:
                    world_data[layer][position.x][position.y]['id'] = id
                    world_data[layer][position.x][position.y]['data'] = block_data
                    
                _run_user_handle(on_block, websocket, world_pb2, player_list, packet.world_block_placed_packet, world_data)
            
            elif packet.HasField("player_direct_message_packet"):
                if commands:
                    for command in commands.keys():
                        if f"//{command}" == packet.player_direct_message_packet.message or f"{packet.player_direct_message_packet.message}".startswith(f"//{command} "):
                            _run_custom_cmd(commands[command], websocket, world_pb2, player_list, packet.player_direct_message_packet.from_player_id, packet.player_direct_message_packet.message, world_data)
            
class Connection:
    def __init__(self, websocket, world_pb2, player_list, world_data):
        self.websocket = websocket
        self.proto = world_pb2
        self.players = player_list
        self.world_data = world_data
    
    def send_chat(self, message):
        packet = self.proto.PlayerChatPacket()
        packet.message = message
        send = self.proto.WorldPacket(player_chat_packet=packet).SerializeToString()
        self.websocket.send(send)
        
    def place_block(self, x, y, layer, id, data=None):
        if layer == 0:
            layer = 'bg'
        if layer == 1:
            layer = 'fg'
        if layer == 2:
            layer = 'ol'
        if not self.world_data[layer][x][y]['id'] == id or not self.world_data[layer][x][y]['data'] == data:
            if layer == 'bg':
                layer = 0
            elif layer == 'fg':
                layer = 1
            elif layer == 'ol':
                layer = 2
                
            data = world.encode_block_placed_data(id, self.world_data['block_list'], data)
                
            packet = self.proto.WorldBlockPlacedPacket()
            packet.block_id = id
            packet.layer = layer
            if data:
                packet.extra_fields = data
            packet.positions.append(self.proto.PointInteger(x=x,y=y))
            send = self.proto.WorldPacket(world_block_placed_packet=packet).SerializeToString()
            self.websocket.send(send)
        
def _run_user_handle(function, websocket, world_pb2, player_list, packet, world_data):
    if function:
        function(Connection(websocket, world_pb2, player_list, world_data), packet)
        
def _run_custom_cmd(function, websocket, world_pb2, player_list, player_id, message, world_data):
    args = message.split(' ')[1:]
    function(Connection(websocket, world_pb2, player_list, world_data), args, player_id)