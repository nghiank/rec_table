from django.db import models

# Create your models here.
class ImageSheet(models.Model):
    """
    Model representing the image uploading by a user
    """
    FRESH='FR'
    PROCESSING='PI'
    PROCESSED='DS'
    PROCESSED_ERROR='DE'
    STATES = (
        (FRESH, 'Fresh'),
        (PROCESSING, 'Processing'),
        (PROCESSED, 'Processed'),
        (PROCESSED_ERROR, 'ProcessedWithError'),
    )
    username = models.CharField(max_length=50, help_text="Username", default='unknown')
    file_id = models.CharField(max_length=120, help_text="File Id")
    url = models.CharField(max_length=500, help_text="File URL")
    state = models.CharField(max_length=2, choices=STATES, default=FRESH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.file_id