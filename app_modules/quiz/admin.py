from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import User, Profile, Quiz, Question, AnswerOption

admin.site.register(User)
admin.site.register(Profile)

class AnswerOptionInline(admin.TabularInline):
    model = AnswerOption
    extra = 4

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerOptionInline]
    list_display = ('text', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)

class QuestionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        valid_forms = [
            form for form in self.forms
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False)
        ]
        if len(valid_forms) < 1:
            raise ValidationError("Квиз должен содержать хотя бы один вопрос.")

class QuestionInline(admin.StackedInline):
    model = Question
    formset = QuestionInlineFormSet
    extra = 1
    min_num = 1
    show_change_link = True

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_by', 'access_token', 'timer')
    list_filter = ('created_by',)
    search_fields = ('title', 'description', 'access_token')
    readonly_fields = ('access_token',)
    inlines = [QuestionInline]

admin.site.register(Quiz, QuizAdmin)
admin.site.register(Question, QuestionAdmin)