from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Favorite(models.Model): 
    team_id = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def get_absolute_url(self): 
        return reverse('/')




class Comment(models.Model): 
    created_on = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game_id = models.IntegerField()
    comment_text = models.TextField(max_length=150)
    
