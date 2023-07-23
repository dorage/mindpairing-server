from django.test import TestCase

from mbti.models import MBTIQuestion, MBTITestThreshold


# Create your tests here.
def testMBTI(answers):
    questions = MBTIQuestion.objects.all()

    if len(answers) != len(questions):
        msg = "Number of 'Questions' and 'Answers' NOT match"

    # {'energy': 0, 'decision': 0, 'information': 0, 'lifestyle': 0,}
    score = {'energy': 0, 'decision': 0, 'information': 0, 'lifestyle': 0, }
    max_score = {'energy': 0, 'decision': 0, 'information': 0, 'lifestyle': 0, }
    for q, a in zip(questions, answers):
        score[q.category] += getattr(q, f"select{a}_score")
        max_score[q.category] += max(q.select0_score, q.select3_score)

    threshold = MBTITestThreshold.objects.first()

    mbti = []

    mbti.append('I') if score['energy'] < threshold.energy else mbti.append('E')
    mbti.append('S') if score['information'] < threshold.information else mbti.append('N')
    mbti.append('T') if score['decision'] < threshold.decision else mbti.append('F')
    mbti.append('P') if score['lifestyle'] < threshold.lifestyle else mbti.append('J')

    result = {
        'score': {
            'energy': f"{score['energy']}/{threshold.energy}/{max_score['energy']}",
            'information': f"{score['information']}/{threshold.information}/{max_score['information']}",
            'decision': f"{score['decision']}/{threshold.decision}/{max_score['decision']}",
            'lifestyle': f"{score['lifestyle']}/{threshold.lifestyle}/{max_score['lifestyle']}",
        },
        'mbti': ''.join(mbti),
    }

    return result


print(testMBTI([0]*20))