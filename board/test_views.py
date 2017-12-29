from django.test import TestCase, Client
from django.core.urlresolvers import reverse
from .models import Scoreboard


class QueryTestCase(TestCase):
    def setUp(self):
        scoreboard = Scoreboard.objects.create(
            num_teams=5, teams=['Coimbatore', 'Cuddalore',
                                'Bangalore', 'OMR', 'Gerukambakkam'],
            num_rounds=4)
        scoreboard.new_board()
        scoreboard.save()
        self.pk = scoreboard.pk
        scoreboard.sent()
        self.client = Client()
    
    def get_scoreboard(self):
        return Scoreboard.objects.get(pk=self.pk)


class ThemeQueryTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': 'default',
                'name': 'set_theme'}
        path = reverse("board:set_theme", kwargs={"pk": self.pk})
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.theme, 'default')
        
        post['choice'] = 'light-blue'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.theme, 'light-blue')
        
        post['choice'] = 'big-bold'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.theme, 'light-blue big-bold')


class OverflowQueryTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': '',
                'name': 'fix_overflow'}
        path = reverse("board:fix_overflow", kwargs={"pk": self.pk})
        
        post['choice'] = 'team1'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.all().count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team1").count(), 1)
        self.assertTrue(scoreboard.is_changed())
        
        post['choice'] = 'team3'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.all().count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell="team1").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team3").count(), 1)
        self.assertTrue(scoreboard.is_changed())


class WinQueryTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': '',
                'name': 'win_animation'}
        path = reverse("board:win_animation", kwargs={"pk": self.pk})
        
        scoreboard = self.get_scoreboard()
        scoreboard.add_question(1, [1, 2, 3, 2, 1])
        scoreboard.save()
        self.client.post(path, data=post)
        self.assertTrue(scoreboard.is_changed())
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.all().count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team3").count(), 1)
        
        scoreboard = self.get_scoreboard()
        scoreboard.add_question(3, [1, 2, 0, 2, 1])
        scoreboard.save()
        self.client.post(path, data=post)  # Should print an error.


class GainLossTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': '', 'points': '',
                'name': 'win_animation'}
        path = reverse("board:gain_loss_animation", kwargs={"pk": self.pk})
        
        post['choice'] = 'team2'
        post['points'] = '15'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.all().count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='team2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=15).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 1)
        
        post['choice'] = 'team1'
        post['points'] = '-2'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.all().count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell='team1').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=-2).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 1)


class PointsChangeTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': '', 'points': '',
                'name': 'points_change'}
        path = reverse("board:points_change", kwargs={"pk": self.pk})
        
        cell = '1,0,3'
        points = 15
        post['points'] = str(points)
        post['choice'] = cell
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            cell=cell).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        
        cell = '4,0,3'
        points = 15
        post['points'] = str(points)
        post['choice'] = cell
        post['pc_animation'] = 'True'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell=cell).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        
        cell = '4,0,3'
        points = -5
        post['points'] = str(points)
        post['choice'] = cell
        post['pc_animation'] = 'True'
        post['gl_animation'] = 'True'
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.count(), 3)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell=cell).count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 1)
        
        cell = '2,0,2'
        points = -29
        post['points'] = str(points)
        post['choice'] = cell
        post['gl_animation'] = 'True'
        post.pop('pc_animation')
        self.client.post(path, data=post)
        scoreboard = self.get_scoreboard()
        self.assertEqual(scoreboard.action_set.count(), 4)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            cell=cell).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 3)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='team2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='team3').count(), 1)


class QuestionQueryTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'team1': '1', 'team2': '2',
                'team3': '1', 'team4': '1', 'team5': '1', 'choice': '2,0,4',
                'name': 'add_question'}
        path = reverse("board:question", kwargs={"pk": self.pk})
        
        rn = 2
        scores = [1, 2, 1, 1, 1]
        pc = False
        gl = False
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        self.client.post(path, data=post)
        self.assertEqual(scoreboard.action_set.count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell=rs).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___scores=scores).count(), 1)
        
        rn = 2
        scores = [1, 2, 0, 0, 1]
        post['team1'] = '1'
        post['team2'] = '2'
        post['team3'] = '0'
        post['team4'] = '0'
        post['team5'] = '1'
        pc = True
        post['pc_animation'] = 'True'
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        self.client.post(path, data=post)
        self.assertEqual(scoreboard.action_set.count(), 8)
        self.assertEqual(scoreboard.action_set.filter(cell=rs).count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 7)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,5').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,1').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,5').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,1').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            name='points_change').count(), 6)
        
        rn = 4
        scores = [1, -39, 0, -2, 15]
        post['team1'] = '1'
        post['team2'] = '-39'
        post['team3'] = '0'
        post['team4'] = '-2'
        post['team5'] = '15'
        post['choice'] = '4,0,0'
        pc = True
        gl = True
        post['gl_animation'] = 'True'
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        self.client.post(path, data=post)
        self.assertEqual(scoreboard.action_set.count(), 21)
        self.assertEqual(scoreboard.action_set.filter(cell=rs).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='gain').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 12)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 4)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 6)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 14)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team1").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team5").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team2").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team4").count(), 1)
        
        rn = 1
        scores = [-1000, 0, 0, 0, 15]
        post['team1'] = '-1000'
        post['team2'] = '0'
        post['team3'] = '0'
        post['team4'] = '0'
        post['team5'] = '15'
        post.pop('pc_animation')
        post['choice'] = '1,0,0'
        pc = False
        gl = True
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        self.client.post(path, data=post)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=0).count(), 0)
        self.assertEqual(scoreboard.action_set.count(), 24)
        self.assertEqual(scoreboard.action_set.filter(cell=rs).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='gain').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 12)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 4)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 7)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 15)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team1").count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team5").count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team2").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            cell="team4").count(), 1)


class SavePointsQueryTestCase(QueryTestCase):
    def test_post_handler(self):
        post = {'csrfmiddlewaretoken': '', 'choice': '', 'points': '',
                'name': 'points_change'}
        path_pc = reverse("board:points_change", kwargs={"pk": self.pk})
        path_save = reverse("board:save_pcs", kwargs={"pk": self.pk})
        
        cell = '1,0,3'
        points = 15
        post['points'] = str(points)
        post['choice'] = cell
        self.client.post(path_pc, data=post)
        self.client.post(path_save, data=post)
