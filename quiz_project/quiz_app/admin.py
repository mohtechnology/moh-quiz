from django.contrib import admin
from .models import Quiz, Question, QuizResult, Student

admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(QuizResult)
admin.site.register(Student)
