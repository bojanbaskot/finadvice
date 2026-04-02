from django.contrib import admin
from .models import CourseCategory, Course, Module, Lesson, Quiz, Question, Answer, QuizAttempt


@admin.register(CourseCategory)
class CourseCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'color']
    prepopulated_fields = {'slug': ('name',)}


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 2
    fields = ['title', 'slug', 'content_type', 'duration_min', 'sort_order', 'is_preview']
    prepopulated_fields = {'slug': ('title',)}


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    fields = ['title', 'sort_order']
    show_change_link = True


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'status', 'is_free']
    list_filter = ['status', 'level', 'category', 'is_free']
    list_editable = ['status', 'is_free']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'sort_order']
    list_filter = ['course']
    inlines = [LessonInline]


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    fields = ['text', 'is_correct', 'sort_order']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    show_change_link = True


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'pass_score', 'time_limit']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['text', 'quiz', 'qtype']
    inlines = [AnswerInline]


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'user', 'score', 'passed', 'created_at']
    list_filter = ['passed', 'quiz']
    readonly_fields = ['quiz', 'user', 'session_key', 'score', 'passed', 'answers_json', 'created_at']
