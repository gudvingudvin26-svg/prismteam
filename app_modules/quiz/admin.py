"""Административная панель для моделей викторин, вопросов и вариантов ответов."""

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet

from .models import AnswerOption, Question, Quiz


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


class QuestionInlineFormSet(BaseInlineFormSet):
    """Кастомный FormSet для валидации вопросов в админ-панели викторины."""

    def clean(self):
        """Проверка, что в админке добавлен хотя бы один вопрос."""
        super().clean()
        # Проверяем формы, которые не помечены на удаление
        valid_forms = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        if len(valid_forms) < 1:
            raise ValidationError("Квиз должен содержать хотя бы один вопрос.")


class QuestionInline(admin.StackedInline):
    """Inline-форма для добавления вопросов на странице редактирования викторины."""
    model = Question
    formset = QuestionInlineFormSet  # Подключаем нашу проверку
    extra = 1
    min_num = 1  # Указывает админке, что поле обязательно (визуально)
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