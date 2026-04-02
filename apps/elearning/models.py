from django.db import models
from django.urls import reverse
from django.contrib.auth import get_user_model
from ckeditor_uploader.fields import RichTextUploadingField
from apps.core.models import TimeStampedModel

User = get_user_model()


class CourseCategory(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#0d6efd')

    class Meta:
        verbose_name = 'Course Category'
        verbose_name_plural = 'Course Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class PublishedCourseManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status='published')


class Course(TimeStampedModel):
    LEVEL_CHOICES = [('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')]
    STATUS_CHOICES = [('draft', 'Draft'), ('published', 'Published')]

    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300, unique=True)
    subtitle = models.CharField(max_length=500, blank=True)
    description = RichTextUploadingField()
    cover_image = models.ImageField(upload_to='courses/', blank=True)
    category = models.ForeignKey(CourseCategory, on_delete=models.PROTECT, related_name='courses')
    instructor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    is_free = models.BooleanField(default=True)
    duration_min = models.PositiveIntegerField(default=0)
    sort_order = models.PositiveSmallIntegerField(default=0)

    objects = models.Manager()
    published = PublishedCourseManager()

    class Meta:
        ordering = ['sort_order', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('elearning:course-detail', kwargs={'slug': self.slug})

    @property
    def lesson_count(self):
        return Lesson.objects.filter(module__course=self).count()


class Module(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=200)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Lesson(TimeStampedModel):
    CONTENT_TYPE_CHOICES = [('text', 'Text'), ('video', 'Video'), ('pdf', 'PDF')]

    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=300)
    slug = models.SlugField(max_length=300)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='text')
    body = RichTextUploadingField(blank=True)
    video_url = models.URLField(blank=True)
    pdf_file = models.FileField(upload_to='lessons/pdfs/', blank=True)
    duration_min = models.PositiveSmallIntegerField(default=0)
    sort_order = models.PositiveSmallIntegerField(default=0)
    is_preview = models.BooleanField(default=False)

    class Meta:
        ordering = ['sort_order']
        unique_together = ('module', 'slug')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('elearning:lesson-detail', kwargs={
            'cslug': self.module.course.slug,
            'slug': self.slug,
        })


class Quiz(TimeStampedModel):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, related_name='quiz',
                                  null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes',
                               null=True, blank=True)
    title = models.CharField(max_length=200)
    pass_score = models.PositiveSmallIntegerField(default=70)
    time_limit = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quizzes'

    def __str__(self):
        return self.title


class Question(models.Model):
    QTYPE_CHOICES = [('single', 'Single Choice'), ('multi', 'Multiple Choice'), ('truefalse', 'True / False')]

    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    qtype = models.CharField(max_length=10, choices=QTYPE_CHOICES, default='single')
    explanation = models.TextField(blank=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.text[:80]


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    sort_order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.text


class QuizAttempt(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    session_key = models.CharField(max_length=40, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    score = models.PositiveSmallIntegerField()
    passed = models.BooleanField()
    answers_json = models.JSONField()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Attempt on {self.quiz.title} - {self.score}%'
