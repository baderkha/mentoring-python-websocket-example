import asyncio
import websockets
import websockets.server
import json


# maintaining connection state (ie a map of all connections)
    # use in memory (use a map)
    # use a database async map
# handling http land connections and checking claims

users = {
    "123":"ahmad",
    "256":"rakan",
    "566" :"admin"
}

# HTTP WORLD 
class MyWebSocketServerProtocol(websockets.server.WebSocketServerProtocol):
    # handles authorization , authentication , ...etc
    async def process_request(self, path, request_headers):
        # Access the HTTP headers here
        token = request_headers["authorization"]

        token = token.replace("Bearer ","")

        if not users[token]:
            response = 'HTTP/1.1 401 Unauthorized\r\n\r\n'
            self.transport.write(response.encode())
            raise websockets.exceptions.ConnectionClosed

        self.user_id = users[token]
        # You can perform some logic based on the headers if needed

        # Call the parent method to continue with the WebSocket handshake
        await super().process_request(path, request_headers)

connections = {}

# handles messages backa and forht
async def handle_connection(websocket, path):
    # when websocket gets created land
    
    connections[websocket.user_id] = websocket
    print(f"user id with id {websocket.user_id} is connected")
    while True:
        # websocket
        message = await websocket.recv()
        # step 1 parse message
        actionData = json.loads(message) 
       
       # step 2 assume this structure
        # {
        #     "action":"message",
        #     "data":{
        #         "user_id" :"rakan",
        #         "message":"you are cool"
        #     }
        # }

        # routing
        if actionData["action"] == "message":
            data = actionData["data"]
            user_id_to_send_to = data["user_id"]
            message = data["message"]
            if not connections[user_id_to_send_to]:
                continue
            peerWebsocket = connections[user_id_to_send_to]
            response = {
                "action":"recieve_messsage",
                "data":{
                    "from":websocket.user_id,
                    "message":message
                }
            }
            await peerWebsocket.send(json.dumps(response))
        elif actionData["action"] == "broadcast" and websocket.user_id == "admin":
            # {
            #     "action":"broadcast",
            #     "data":{
            #         "message" : "something"
            #     }
            # }
            message = actionData["data"]["message"]
            response = {
                "action":"recieve_broadcast",
                "data":{
                    "message":message
                }
            }
            responseStr = json.dumps(response)
            for key,wsCon in connections.items() :
                await wsCon.send(responseStr)
        else:
            await websocket.send("unexpected")

        # Send a response back to the client
        response = f"Server received: {message}"
        

async def main():
    server = await websockets.serve(handle_connection, "localhost", 7005,create_protocol=MyWebSocketServerProtocol)

    print("WebSocket server started. Listening on ws://localhost:7005")

    await server.wait_closed()

if __name__ == "__main__":
    asyncio.run(main())
