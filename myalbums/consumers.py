
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from .models import Profile, Comment, Review , User
# from django.contrib.auth.models import User
from django.template.loader import render_to_string
# from django.db.models import Avg
# from django.core.exceptions import ValidationError
from django.contrib import messages
from django.http import JsonResponse

from django.http import HttpResponse

class ReviewConsumer(WebsocketConsumer):
    def connect(self):
        print("ok connect")
        self.review_name = self.scope['url_route']['kwargs']['review_name']
        self.review_group_name = 'chat_%s' % self.review_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.review_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        print("close connect")
        async_to_sync(self.channel_layer.group_discard)(
            self.review_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        print("\nstart receive data from song_detail")
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        # vote = float(text_data_json['vote'])
        print(content)
        reviewId = text_data_json['reviewId']
        print(reviewId)
        userId = text_data_json['userId']
        print(userId)
        print("finis reciew\n")
        user = User.objects.get(id=userId)
        review = Review.objects.get(id=reviewId)

        comment = Comment(user = user, review = review, text = content)
        comment.save()

        commentInfor = {
            'id' : comment.id,
        }
        commentInfor = json.dumps(commentInfor)
        htmlRender = render_to_string("myalbums/comments.html",{'comment':comment})

        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.review_group_name,
            {
                'type': 'chat_message',
                'comment': commentInfor,
                'htmlRender' : htmlRender
            }
        )

    # # Receive message from room group
    def chat_message(self, event):
        print("ok chat")
        comment = event['comment']
        htmlRender = event['htmlRender']
        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'comment': comment,
            'htmlRender' : htmlRender,
        }))

