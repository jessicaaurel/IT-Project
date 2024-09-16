# Generated by Django 5.1.1 on 2024-09-16 09:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gameresult',
            name='outcome',
            field=models.CharField(choices=[('P1', 'Player 1 Wins'), ('P2', 'Player 2 Wins'), ('draw', 'Draw')], max_length=4),
        ),
    ]
