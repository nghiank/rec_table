from django.db import models

# Create your models here.
class ImageSheet(models.Model):
    """
    Model representing the image uploading by a user
    """
    url = models.CharField(max_length=200, help_text="S3 Url")
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.url