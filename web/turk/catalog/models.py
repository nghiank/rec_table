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
    url = models.CharField(max_length=254, help_text="File URL")
    state = models.CharField(max_length=20, choices=STATES, default=FRESH)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        """
        String for representing the Model object (in Admin site etc.)
        """
        return self.file_id

class Cell(models.Model):
    """
    Model representing the cell we extracted from ImageSheet
    """
    url = models.CharField(max_length=254, help_text="File URL")
    file_path = models.CharField(max_length=254, help_text="S3 relative file path")
    expected_char = models.CharField(max_length=1, help_text="Expected character")
    predicted_char = models.CharField(max_length=1, help_text="Predicted_character")
    image_sheet = models.ForeignKey(ImageSheet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.url
    class Meta:
        unique_together = ('image_sheet', 'file_path')

class ExpectedResult(models.Model):
    """
    Model representing the full expected result of the ImageSheet
    """
    order = models.IntegerField()
    num = models.CharField(max_length=4, help_text="Number field")
    big = models.CharField(max_length=3, help_text="Big number field")
    small = models.CharField(max_length=3, help_text="Small number field")
    roll = models.CharField(max_length=1, help_text="Roll field R,K,I,r,k,i")
    is_delete = models.CharField(max_length=1, help_text="is this line deleted")
    image_sheet = models.ForeignKey(ImageSheet, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('image_sheet', 'order')

class UserNeuralNet(models.Model):
    """
    Model representing the neural net customized for each user
    """
    username = models.CharField(max_length=50, help_text="Username")
    data_name = models.CharField(max_length=20, help_text="Data name")
    file_path = models.CharField(max_length=254, help_text="S3 relative file path")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('username', 'data_name')
    