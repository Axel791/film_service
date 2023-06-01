import datetime
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender='movies.FilmWork')
def attention(sender, instance, created, **kwargs):
    if created and instance.created == datetime.date.today():
        print(f"Сегодня премьера {instance.title}! 🥳")
