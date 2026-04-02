from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Course, CourseCategory, Module, Lesson, Quiz, Question, Answer, QuizAttempt


class CourseListView(ListView):
    model = Course
    template_name = 'elearning/course_list.html'
    context_object_name = 'courses'
    paginate_by = 9

    def get_queryset(self):
        qs = Course.published.all().select_related('category', 'instructor')
        category = self.request.GET.get('kategorija')
        level = self.request.GET.get('nivo')
        if category:
            qs = qs.filter(category__slug=category)
        if level:
            qs = qs.filter(level=level)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['categories'] = CourseCategory.objects.all()
        ctx['levels'] = Course.LEVEL_CHOICES
        return ctx


class CourseDetailView(DetailView):
    model = Course
    template_name = 'elearning/course_detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        return Course.published.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        course = self.object
        ctx['modules'] = course.modules.prefetch_related('lessons').all()
        ctx['quizzes'] = course.quizzes.all()
        return ctx


class LessonDetailView(View):
    template_name = 'elearning/lesson_detail.html'

    def get(self, request, cslug, slug):
        course = get_object_or_404(Course.published, slug=cslug)
        lesson = get_object_or_404(Lesson, slug=slug, module__course=course)
        modules = course.modules.prefetch_related('lessons').all()
        return render(request, self.template_name, {
            'course': course,
            'lesson': lesson,
            'modules': modules,
        })


class QuizView(View):
    template_name = 'elearning/quiz_detail.html'

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        questions = quiz.questions.prefetch_related('answers').all()
        return render(request, self.template_name, {'quiz': quiz, 'questions': questions})


class QuizSubmitView(View):
    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        questions = quiz.questions.prefetch_related('answers').all()
        total = questions.count()
        if total == 0:
            return redirect('elearning:quiz-result', pk=pk)

        correct_count = 0
        answers_snapshot = []

        for question in questions:
            correct_ids = set(question.answers.filter(is_correct=True).values_list('id', flat=True))
            submitted_raw = request.POST.getlist(f'q_{question.pk}')
            submitted_ids = set(int(x) for x in submitted_raw if x.isdigit())
            is_correct = submitted_ids == correct_ids
            if is_correct:
                correct_count += 1
            answers_snapshot.append({
                'question_id': question.pk,
                'question_text': question.text,
                'submitted': list(submitted_ids),
                'correct': list(correct_ids),
                'is_correct': is_correct,
                'explanation': question.explanation,
            })

        score = int((correct_count / total) * 100)
        passed = score >= quiz.pass_score
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            session_key=request.session.session_key or '',
            user=request.user if request.user.is_authenticated else None,
            score=score,
            passed=passed,
            answers_json=answers_snapshot,
        )
        return redirect('elearning:quiz-result', pk=attempt.pk)


class QuizResultView(DetailView):
    model = QuizAttempt
    template_name = 'elearning/quiz_result.html'
    context_object_name = 'attempt'
