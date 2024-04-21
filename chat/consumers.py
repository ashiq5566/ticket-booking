import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from api.v1.chat.functions import get_station_list


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'chat-bot-{self.user_id}'
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )


    def receive(self, text_data):
        json_text = json.loads(text_data)
        message = json_text["message"]
       
        start_station = self.scope.get('start_station', "")

        if message == 'hi':
            # Respond with initial options
            response_message = "Select below options:\n1. Book ticket"
        elif message == '1':
            # Respond with start stations list
            start_stations = get_station_list(start_station)
            response_message = "Select a start station:\n{}".format(", ".join(start_stations))
        elif start_station and message in start_stations:
            # User has selected a start station, retrieve end stations
            end_stations = get_station_list(start_station)
            response_message = "End stations for {}:\n{}".format(start_station, ", ".join(end_stations))
        elif start_station and message in end_stations:
            # User has selected an end station, calculate trip amount
            trip_amount = 100
            response_message = "Trip amount for {} to {} is: ${}".format(start_station, message, trip_amount)
        else:
            # Invalid input message
            response_message = "Invalid input. Please try again."

        # Send response to the group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': response_message
            }
        )
        
        
        # # Send message to room group
        # async_to_sync(self.channel_layer.group_send)(
        #     self.room_group_name, 
        #     {
        #         "type": "chat_message", 
        #         "message": f'recieved:{message}'
        #     }
        # )
    
    def chat_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        self.send(text_data=json.dumps({"message": message}))