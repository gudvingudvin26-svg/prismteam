"""Административная панель Django для управления сущностями квиз-приложения.

Настраивает отображение и редактирование моделей User, Profile, Quiz,
Question, AnswerOption в Django Admin. Включает inline-редактирование
вопросов и вариантов ответов, валидацию минимального количества вопросов,
фильтрацию и поиск для удобного управления контентом.
"""
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import User, Profile, Quiz, Question, AnswerOption


admin.site.register(User)
admin.site.register(Profile)


class AnswerOptionInline(admin.TabularInline):
    """Inline-редактор вариантов ответов для отображения внутри вопроса.

    Использует табличный вид (TabularInline) для компактного редактирования.
    По умолчанию показывает 4 пустых поля для добавления новых вариантов.
    """
    model = AnswerOption
    extra = 4


class QuestionAdmin(admin.ModelAdmin):
    """Настройка админки для модели Question.

    Включает inline-редактирование вариантов ответов, отображение ключевых
    полей в списке, фильтрацию по квизу и поиск по тексту вопроса.
    """
    inlines = [AnswerOptionInline]
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)


class QuestionInlineFormSet(BaseInlineFormSet):
    """Кастомный FormSet для валидации inline-вопросов в квизе.

    Переопределяет метод clean() для проверки бизнес-правила:
    квиз должен содержать минимум один вопрос при сохранении.
    Игнорирует помеченные на удаление формы при подсчёте.
    """
    def clean(self):
        """Валидация: проверка наличия хотя бы одного не удалённого вопроса."""
        super().clean()
        valid_forms = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        if len(valid_forms) < 1:
            raise ValidationError("Квиз должен содержать хотя бы один вопрос.")


class QuestionInline(admin.StackedInline):
    """Inline-редактор вопросов для отображения внутри квиза.

    Использует блочный вид (StackedInline) для удобного редактирования
    сложных вопросов с вариантами ответов. Применяет кастомный FormSet
    для валидации минимального количества вопросов.
    """
    model = Question
    formset = QuestionInlineFormSet
    extra = 1
    min_num = 1
    show_change_link = True


class QuizAdmin(admin.ModelAdmin):
    """Настройка админки для модели Quiz.

    Отображает ключевые поля в списке, включает фильтрацию по создателю,
    поиск по названию/описанию/токену. Поле access_token доступно только
    для чтения. Включает inline-редактирование вопросов с валидацией.
    """
    list_display = ('title', 'created_by', 'access_token', 'timer')
    list_filter = ('created_by',)
    search_fields = ('title', 'description', 'access_token')
    readonly_fields = ('access_token',)
    inlines = [QuestionInline]


admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)