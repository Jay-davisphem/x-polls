import datetime
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice
from django.contrib.auth.models import User


class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """ was_published_recently() returns False for questions whose pub_date is older than 1 day. """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """ was_published_recently() returns True for questions whose pub_date is within the last day. """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def test_question_str(self):
        question = Question(question_text='This is a question.')
        self.assertEqual(question.__str__(), 'This is a question.')


def create_question(question_text, days, choice=True):
    pub_date = timezone.now() + datetime.timedelta(days)
    question = Question.objects.create(
        question_text=question_text, pub_date=pub_date)
    if choice:
        question.choice_set.create(choice_text='answer one')
    return question


class ChoiceModelTests(TestCase):
    def test_choice_str(self):
        question = Question(question_text='This is a question.')
        question.save()
        question.choice_set.create(choice_text='Yes, it is!')
        question.save()
        self.assertEqual(question.choice_set.get(
            pk=1).__str__(), 'Yes, it is!')


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """ If no questions exist, an appropriate message is displayed. """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """ Questions with a pub_date in the past are displayed on the index page. """
        create_question(question_text="Past question.", days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question.>'])

    def test_future_question(self):
        """ Questions with a pub_date in the future aren't displayed on the index page. """
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """ Even if both past and future questions exist, only past questions are displayed. """
        create_question(question_text="Past question.", days=-30)
        create_question(question_text="Future question.", days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question.>'])

    def test_two_past_questions(self):
        """ The questions index page may display multiple questions. """
        create_question(question_text="Past question 1.", days=-30)
        create_question(question_text="Past question 2.", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], [
                                 '<Question: Past question 2.>', '<Question: Past question 1.>'])

    def test_questions_has_no_choice(self):
        create_question(question_text='Question 1', days=0, choice=False)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")

    def test_unpublished_is_seen_by_admin_user(self):
        user = User.objects.create_user(
            username='davisphem', password='phemmy2022', is_staff=True)
        user.save()
        create_question(question_text='Question 1', days=30, choice=False)
        self.client.login(username='davisphem', password='phemmy2022')
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [
            '<Question: Question 1>'])


class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """ The detail view of a question with a pub_date in the future returns a 404 not found. """
        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """ The detail view of a question with a pub_date in the past displays the question's text. """
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_questions_has_no_choice(self):
        question = create_question(
            question_text='Question 1', days=0, choice=False)
        response = self.client.get(
            reverse('polls:detail', args=(question.id, )))
        self.assertEqual(response.status_code, 404)


class QuestionResultViewTests(TestCase):
    def test_futrure_question(self):
        future_question = create_question(
            question_text='Future question.', days=5)
        url = reverse('polls:results', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """ The result view of a question with a pub_date in the past displays the results. """
        past_question = create_question(
            question_text='Past Question.', days=-5)
        url = reverse('polls:results', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

    def test_questions_has_no_choice(self):
        question = create_question(
            question_text='Question 1', days=0, choice=False)
        response = self.client.get(
            reverse('polls:results', args=(question.id, )))
        self.assertEqual(response.status_code, 404)
