from django.db import models

class TripRequest(models.Model):
    """Stores trip planning requests for analytics."""
    name = models.CharField(max_length=200)
    budget = models.FloatField()
    currency = models.CharField(max_length=10, default='INR')
    travel_type = models.CharField(max_length=20)  # solo/group
    group_size = models.IntegerField(default=1)
    travel_scope = models.CharField(max_length=30)  # within_country/outside_country
    num_days = models.IntegerField()
    food_accommodation = models.CharField(max_length=20)
    from_location = models.CharField(max_length=200)
    travel_medium = models.CharField(max_length=50)
    destination_styles = models.JSONField(default=list)
    ip_address = models.CharField(max_length=50, blank=True)
    ip_location = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.from_location} ({self.created_at.strftime('%Y-%m-%d')})"


class ContactMessage(models.Model):
    """Stores contact form submissions from the website."""
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        status = '✓' if self.is_read else '●'
        return f"{status} {self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
