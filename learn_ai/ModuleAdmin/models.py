from django.db import models

# Create your models here.
class Course(models.Model):
    id=models.AutoField(primary_key=True)
    course_name=models.CharField(max_length=100)
    description=models.TextField()
    course_image=models.ImageField(upload_to='images/')
    created_at=models.DateTimeField(auto_now_add=True)
    youtube_link=models.URLField(blank=True)
    pdf_documents=models.FileField(upload_to='pdfs/')
    
    def __str__(self):
        return self.course_name
    
    
class ChatMessage(models.Model):
    role = models.CharField(max_length=10, choices=[('user', 'User'), ('assistant', 'Assistant')])
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
    
class PDFFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_id = models.CharField(max_length=255)

    def __str__(self):
        return self.file_name