from django.db import models
from django.contrib.auth.models import User

class Quiz(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit = models.IntegerField()
    quiz_password = models.CharField(max_length=100)

class Student(models.Model):
    enrollment = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    email = models.EmailField()
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.enrollment} - {self.name}"

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()  # Question text
    option1 = models.CharField(max_length=255)
    option2 = models.CharField(max_length=255)
    option3 = models.CharField(max_length=255)
    option4 = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=255)  # Store the correct answer as text

    def __str__(self):
        return self.text

class QuizResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    score = models.IntegerField()
    total_questions = models.IntegerField()
    date_attempted = models.DateTimeField(auto_now_add=True)
    time_taken = models.IntegerField(help_text="Time taken in seconds")  # New field

    def __str__(self):
        return f"{self.student.name} - {self.quiz.title} - Score: {self.score} - Time: {self.time_taken} sec"

