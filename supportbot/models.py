from django.db import models


class InquiryLog(models.Model):
    class Channel(models.TextChoices):
        LINE = 'line', 'LINE'
        WEBFORM = 'webform', 'Web form'

    class Status(models.TextChoices):
        AUTO_REPLY = 'auto_reply', 'Auto reply'
        ESCALATION = 'escalation', 'Escalation'

    channel = models.CharField(max_length=20, choices=Channel.choices)
    contact = models.CharField(max_length=255, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices)
    generated_reply = models.TextField()
    matched_knowledge = models.CharField(max_length=255, blank=True)
    escalation_target = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.channel}:{self.status}:{self.contact or "anonymous"}'
