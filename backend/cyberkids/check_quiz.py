from apps.quiz.models import Quiz, QuizQuestion, QuizAlternative

q = Quiz.objects.first()
print(f'\n=== QUIZ: {q.title} ===')
print(f'Total preguntas: {q.questions.count()}')

for question in q.questions.all()[:3]:
    print(f'\nPregunta {question.display_order}: {question.content[:60]}...')
    print(f'  Explanation: {question.explanation[:60] if question.explanation else "None"}...')
    print(f'  Alternativas: {question.alternatives.count()}')
    
    for alt in question.alternatives.all():
        correct = "✓" if alt.is_correct else " "
        print(f'    [{correct}] {alt.content[:50]}...')
        print(f'        Feedback: {alt.feedback[:50] if alt.feedback else "None"}...')
