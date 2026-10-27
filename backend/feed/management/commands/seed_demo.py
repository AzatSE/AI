from django.core.management.base import BaseCommand
from feed.models import Post

class Command(BaseCommand):
    help = 'Create demo posts, only when the feed is empty.'
    def handle(self, *args, **options):
        if Post.objects.exists():
            self.stdout.write('Feed already populated; leaving it unchanged.')
            return
        demo = [
            ('Aurelia Studio', 'aureliastudio', 'A small reminder: you don’t have to have it all figured out to create something beautiful. Just start. ✧\n\n#MadeOfStardust', 'photo-1470252649378-9c29740c9fa8', 86),
            ('David Chen', 'davidchen', 'Somewhere between the mountains and the morning light, everything made sense.\n\n#ThroughMyLens', 'photo-1464822759023-fed622ff2c3b', 128),
            ('Elena Rivers', 'elenarivers', 'Maybe we’re all just little universes, looking for a place to collide. ✨\n\n#MadeOfStardust', '', 214),
            ('NASA', 'nasa', 'A little perspective from the universe. ✨\nThousands of stars. Endless possibilities. And you, right here, being part of it all.\n\n#BeyondTheStars', 'photo-1462331940025-496dfbfc7564', 1248),
        ]
        for author, handle, text, image, likes in demo:
            Post.objects.create(author=author, handle=handle, text=text, image=f'https://images.unsplash.com/{image}?auto=format&fit=crop&w=1200&q=85' if image else '', likes=likes)
        self.stdout.write(self.style.SUCCESS('Created four demo posts.'))
