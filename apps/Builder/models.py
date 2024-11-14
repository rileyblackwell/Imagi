# builder/models.py

from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} for {self.user.username}"


class Page(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="pages")
    filename = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['conversation', 'filename']

    def __str__(self):
        return f"Page {self.filename} in Conversation {self.conversation.id}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name="messages", null=True)
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant'), ('system', 'System')])
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role.capitalize()} message for {self.page.filename if self.page else 'unknown page'}"
