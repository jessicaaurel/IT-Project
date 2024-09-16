from django.db import models
from django.contrib.auth.models import User

class GameResult(models.Model):
    OUTCOME_CHOICES = [
        ('P1', 'Player 1 Wins'),
        ('P2', 'Player 2 Wins'),
        ('draw', 'Draw'),
    ]
    
    player_one = models.ForeignKey(User, related_name='games_as_player_one', on_delete=models.CASCADE)
    player_two = models.ForeignKey(User, related_name='games_as_player_two', on_delete=models.CASCADE)
    outcome = models.CharField(max_length=4, choices=OUTCOME_CHOICES)
    game_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Match between {self.player_one.username} and {self.player_two.username} on {self.game_date}"
