from django.db import models
from django.contrib.auth.models import User

class GameResult(models.Model):
    OUTCOME_CHOICES = [
        ('P1', 'Player 1 Wins'),
        ('P2', 'Player 2 Wins'),
        ('draw', 'Draw'),
    ]
    
    player_one = models.ForeignKey(User, related_name='games_as_player_one', on_delete=models.CASCADE, null=True, blank=True)
    player_two = models.ForeignKey(User, related_name='games_as_player_two', on_delete=models.CASCADE, null=True, blank=True)
    ai_model1 = models.CharField(max_length=100, null=True, blank=True)
    ai_model2 = models.CharField(max_length=100, null=True, blank=True)
    outcome = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    game_date = models.DateField(auto_now_add=True)

    def __str__(self):

        print("MODEL 1: " + self.ai_model1)
        print("MODEL 2: " + self.ai_model2)

        if (self.ai_model1 and self.ai_model2):
            print("MODEL SUCCESS")
            return f"Match between {self.ai_model1} and {self.ai_model2} on {self.game_date}"
        return f"Match between {self.player_one.username} and AI model {self.ai_model2} on {self.game_date}"
        