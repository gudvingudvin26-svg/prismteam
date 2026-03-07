from django.contrib import admin
from .models import Quiz, Question, AnswerOption


class AnswerOptionInline(admin.TabularInline):
    """
    Inline-форма для добавления вариантов ответов на странице редактирования вопроса.
    """
    model = AnswerOption
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Question.
    """
    inlines = [AnswerOptionInline]
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)


class QuestionInline(admin.StackedInline):
    """
    Inline-форма для добавления вопросов на странице редактирования викторины.
    """
    model = Question
    extra = 1
    show_change_link = True


class QuizAdmin(admin.ModelAdmin):
    """
    Административная панель для модели Quiz.
    """
    list_display = ('title', 'created_by', 'access_token')
    list_filter = ('created_by',)
    search_fields = ('title', 'description', 'access_token')
    readonly_fields = ('access_token',)  # Не позволит менять токен вручную
    inlines = [QuestionInline]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)