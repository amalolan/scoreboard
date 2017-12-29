from django.test import TestCase
from .models import *
from copy import deepcopy


# TODO: Test with total_rounds > 9 and total_teams > 9

class ScoreboardTestCase(TestCase):
    
    def setUp(self):
        scoreboard = Scoreboard.objects.create(
            num_teams=5, teams=['Coimbatore', 'Cuddalore',
                                'Bangalore', 'OMR', 'Gerukambakkam'],
            num_rounds=4)
        scoreboard.new_board()
        scoreboard.save()
        self.pk = scoreboard.pk
        scoreboard.sent()
    
    def get_scoreboard(self):
        return Scoreboard.objects.get(pk=self.pk)
    
    def test_set_theme(self):
        scoreboard = self.get_scoreboard()
        
        scoreboard.set_theme('default')
        self.assertEqual(scoreboard.theme, 'default')
        
        scoreboard.set_theme('light-blue')
        self.assertEqual(scoreboard.theme, 'light-blue')
        
        scoreboard.set_theme('big-bold')
        self.assertEqual(scoreboard.theme, 'light-blue big-bold')
        
        scoreboard.set_theme('light-brown')
        self.assertEqual(scoreboard.theme, 'light-brown big-bold')
        
        scoreboard.set_theme('big-bold')
        self.assertEqual(scoreboard.theme, 'light-brown')
        
        scoreboard.set_theme('big-bold')
        self.assertEqual(scoreboard.theme, 'light-brown big-bold')
        
        scoreboard.set_theme('default')
        self.assertEqual(scoreboard.theme, 'default big-bold')
        
        scoreboard.save()
        self.assertTrue(scoreboard.is_changed())
    
    def test_fix_overflow(self):
        scoreboard = self.get_scoreboard()
        
        scoreboard.fix_overflow('team3')
        self.assertEqual(scoreboard.action_set.all().count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team1").count(), 0)
        self.assertEqual(scoreboard.action_set.filter(cell="team3").count(), 1)
        
        scoreboard.fix_overflow('team1')
        self.assertEqual(scoreboard.action_set.all().count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell="team1").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team3").count(), 1)
        
        scoreboard.fix_overflow('team3')
        self.assertEqual(scoreboard.action_set.all().count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell="team1").count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell="team3").count(), 1)
    
    def test_add_question(self):
        scoreboard = self.get_scoreboard()
        
        board = deepcopy(scoreboard.board)
        round_num = 2
        question = ['Question 1', 1, 2, 3, 4, 5]
        board[round_num].append(question)
        scoreboard.add_question(round_num, question[1:])
        self.assertEqual(board, scoreboard.board)
        
        board = deepcopy(scoreboard.board)
        round_num = 2
        question = ['Question 2', 1, 2, 3, 4, 5]
        board[round_num].append(question)
        scoreboard.add_question(round_num, [str(i) for i in question[1:]])
        self.assertEqual(board, scoreboard.board)
        
        round_num = 183
        with self.assertRaises(AssertionError):
            scoreboard.add_question(round_num, question)
        
        round_num = 0
        question = [1, 2, 3, 4, 5, 6, 7, 8]
        with self.assertRaises(AssertionError):
            scoreboard.add_question(round_num, question)
        
        round_num = 3
        question = [1, 2]
        with self.assertRaises(AssertionError):
            scoreboard.add_question(round_num, question)
        
        question = []
        with self.assertRaises(AssertionError):
            scoreboard.add_question(round_num, question)
    
    def test_get_sum(self):
        scoreboard = self.get_scoreboard()
        
        board = deepcopy(scoreboard.board)
        round_num = 2
        question = ['Question 1', 1, 10, 0, 1, 0]
        board[round_num].append(question)
        board[round_num][0][1:] = question[1:]
        scoreboard.add_question(round_num, question[1:])
        self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        board = deepcopy(scoreboard.board)
        question = ['Question 2', 0, 1, 2, 0, 1]
        board[round_num].append(question)
        board[round_num][0][1:] = [1, 11, 2, 1, 1]
        scoreboard.add_question(round_num, question[1:])
        self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        board = deepcopy(scoreboard.board)
        round_num = 3
        question = ['Question 1', 0, 1, 2, 0, 1]
        board[round_num].append(question)
        board[round_num][0][1:] = question[1:]
        scoreboard.add_question(round_num, question[1:])
        self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        board = deepcopy(scoreboard.board)
        round_num = 0
        board[round_num][0][1:] = [1, 12, 4, 1, 2]
        self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        board = deepcopy(scoreboard.board)
        round_num = -1
        
        with self.assertRaises(AssertionError):
            self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        board = deepcopy(scoreboard.board)
        round_num = 3114
        
        with self.assertRaises(AssertionError):
            self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
        
        with self.assertRaises(AssertionError):
            self.assertEqual(scoreboard.get_sum(round_num), board[round_num][0])
    
    def test_get_winner(self):
        scoreboard = self.get_scoreboard()
        scoreboard.add_question(1, [1, 2, 3, 4, 5])
        self.assertEqual(scoreboard.get_winner(), 'team5')
        
        scoreboard = self.get_scoreboard()
        scoreboard.add_question(2, [1, 2, 3, 4, 1])
        self.assertEqual(scoreboard.get_winner(), 'team4')
        
        scoreboard.new_board()
        scoreboard = self.get_scoreboard()
        scoreboard.add_question(1, [1, 2, 5, 4, 5])
        
        with self.assertRaises(AssertionError):
            scoreboard.get_winner()
        
        scoreboard.new_board()
        scoreboard = self.get_scoreboard()
        
        with self.assertRaises(AssertionError):
            scoreboard.get_winner()
    
    def test_gain_loss_animation(self):
        team = 'team3'
        points = 15
        scoreboard = self.get_scoreboard()
        scoreboard.gain_loss_animation(team, points)
        
        self.assertEqual(scoreboard.action_set.all().count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell=team).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 1)
        
        team = 'team3'
        points = -15
        scoreboard = self.get_scoreboard()
        scoreboard.gain_loss_animation(team, points)
        
        self.assertEqual(scoreboard.action_set.all().count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell=team).count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 1)
        
        team = 'team1'
        points = 29
        scoreboard = self.get_scoreboard()
        scoreboard.gain_loss_animation(team, points)
        
        self.assertEqual(scoreboard.action_set.all().count(), 3)
        self.assertEqual(scoreboard.action_set.filter(cell=team).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___points=points).count(), 1)
        
        scoreboard.fix_overflow('team3')
        self.assertEqual(scoreboard.action_set.all().count(), 4)
        self.assertEqual(scoreboard.action_set.filter(cell=team).count(), 1)
        
        team = 'team3'
        points = 0
        scoreboard = self.get_scoreboard()
        
        with self.assertRaises(AssertionError):
            scoreboard.gain_loss_animation(team, points)
    
    def test_change_points(self):
        coords = [[1, 0, 1], [3, 0, 2], [2, 0, 2], [4, 0, 3]]
        points = [10, 15, 15, -15]
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[1][0][1] = 10
        board[3][0][2] = 15
        board[2][0][2] = 15
        board[4][0][3] = -15
        board[0][0][1] = 10
        board[0][0][2] = 30
        board[0][0][3] = -15
        scoreboard.change_points(coords, points)
        self.assertEqual(scoreboard.board, board)
        
        coords = [[1, 0, 1]]
        points = [10]
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[1][0][1] = 10
        board[0][0][1] = 10
        scoreboard.change_points(coords, points)
        self.assertEqual(scoreboard.board, board)
        
        coords = [[1, 0, 1]]
        points = [0]
        scoreboard.change_points(coords, points)
        self.assertEqual(scoreboard.board, board)
    
    def test_points_change(self):
        cell = '1,0,3'
        coords = [int(i) for i in cell.split(',')]
        points = 15
        pc_animation = False
        gl_animation = False
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[coords[0]][0][coords[2]] += points
        board[0][0][coords[2]] += points
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(scoreboard.action_set.count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        
        cell = '2,0,2'
        coords = [int(i) for i in cell.split(',')]
        points = -15
        pc_animation = True
        gl_animation = False
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[coords[0]][0][coords[2]] += points
        board[0][0][coords[2]] += points
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(scoreboard.action_set.count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=False).count(), 1)
        
        # If pc_animation and gl_animation are true, check if GLAction object is
        # created and if PCAction object has animate_type set to gain/loss.
        cell = '3,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = True
        gl_animation = True
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[coords[0]][0][coords[2]] += points
        board[0][0][coords[2]] += points
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(scoreboard.action_set.count(), 3)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=False).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=True).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(cell='team5').count(), 1)
        
        # If pc_animation is False, but gl_animation is true, check if GLAction
        # object is still created.
        cell = '4,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = False
        gl_animation = True
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[coords[0]][0][coords[2]] += points
        board[0][0][coords[2]] += points
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(scoreboard.action_set.count(), 4)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=False).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=True).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 3)
        
        cell = '4,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = -20
        pc_animation = False
        gl_animation = True
        scoreboard = self.get_scoreboard()
        board = deepcopy(scoreboard.board)
        board[coords[0]][0][coords[2]] += points
        board[0][0][coords[2]] += points
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        scoreboard.save()
        scoreboard.fix_overflow('team5')
        self.assertEqual(scoreboard.action_set.count(), 6)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___points=points).count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='loss').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=False).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___gl_animation=True).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='loss').count(), 2)
        self.assertEqual(scoreboard.action_set.filter(
            GainLossAction___animation_type='gain').count(), 3)
    
    def test_question(self):
        rn = 2
        scores = [1, 2, 1, 1, 1]
        pc = False
        gl = False
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        scoreboard.question(rn, scores, pc, gl)
        self.assertEqual(scoreboard.action_set.count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell=rs).count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___scores=scores).count(), 1)
        scoreboard.save()
        
        rn = 2
        scores = [1, 2, 0, 0, 1]
        pc = True
        gl = False
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        scoreboard.question(rn, scores, pc, gl)
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
        scoreboard.save()
        
        rn = 4
        scores = [1, -39, 0, -2, 15]
        pc = True
        gl = True
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        scoreboard.question(rn, scores, pc, gl)
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
        scoreboard.save()
        
        rn = 1
        scores = [-1000, 0, 0, 0, 15]
        pc = False
        gl = True
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        scoreboard.question(rn, scores, pc, gl)
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
        scoreboard.save()
        
        self.setUp()
        
        rn = 2
        scores = [1, 2, 3, 4, 5]
        pc = True
        gl = False
        scoreboard = self.get_scoreboard()
        rs = str(rn) + ",0"
        scoreboard.question(rn, scores, pc, gl)
        self.assertEqual(scoreboard.action_set.count(), 11)
        self.assertEqual(scoreboard.action_set.filter(
            QuestionAction___animation_type='null').count(), 0)
        self.assertEqual(scoreboard.action_set.filter(
            PointsChangeAction___animation_type='gain').count(), 11)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,5').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,1').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='2,0,2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,5').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,1').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(cell='0,0,2').count(), 1)
        self.assertEqual(scoreboard.action_set.filter(
            name='points_change').count(), 10)
    
    def test_save_points_changes(self):
        scoreboard = self.get_scoreboard()
        cell = '1,0,3'
        coords = [int(i) for i in cell.split(',')]
        points = 15
        pc_animation = False
        gl_animation = False
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(len(scoreboard.history), 1)
        self.assertEqual(scoreboard.history[-1].get('points'), points)
        scoreboard.save_points_changes()
        self.assertEqual(len(scoreboard.history), 1)
        self.assertIsNone(scoreboard.history[-1].get('points'))
        self.assertEqual(scoreboard.history[-1].get('scores'), [0, 0, 15, 0, 0])
        self.assertEqual(scoreboard.history[-1].get('round_num'), coords[0])
        self.assertEqual(scoreboard.history[-1].get('question_num'), 1)
        scoreboard.save()

        scoreboard = self.get_scoreboard()
        cell = '1,0,2'
        coords = [int(i) for i in cell.split(',')]
        points = -30
        pc_animation = True
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '1,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(len(scoreboard.history), 3)
        self.assertEqual(scoreboard.history[-1].get('points'), points)
        self.assertEqual(scoreboard.history[-2].get('points'), -30)
        scoreboard.save_points_changes()
        self.assertEqual(len(scoreboard.history), 2)
        self.assertIsNone(scoreboard.history[-1].get('points'))
        self.assertEqual(scoreboard.history[-1].get('scores'), [0, -30, 0, 0, 1])
        self.assertEqual(scoreboard.history[-1].get('round_num'), coords[0])
        self.assertEqual(scoreboard.history[-1].get('question_num'), 2)
        scoreboard.save()

        scoreboard = self.get_scoreboard()
        cell = '2,0,2'
        coords = [int(i) for i in cell.split(',')]
        points = -30
        pc_animation = True
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '2,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '2,0,1'
        coords = [int(i) for i in cell.split(',')]
        points = 12
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(len(scoreboard.history), 5)
        self.assertEqual(scoreboard.history[-1].get('points'), points)
        self.assertEqual(scoreboard.history[-2].get('points'), 1)
        scoreboard.save_points_changes()
        self.assertEqual(len(scoreboard.history), 3)
        self.assertIsNone(scoreboard.history[-1].get('points'))
        self.assertEqual(scoreboard.history[-1].get('scores'), [12, -30, 0, 0, 1])
        self.assertEqual(scoreboard.history[-1].get('round_num'), coords[0])
        self.assertEqual(scoreboard.history[-1].get('question_num'), 1)
        scoreboard.save()

        scoreboard = self.get_scoreboard()
        cell = '3,0,2'
        coords = [int(i) for i in cell.split(',')]
        points = -30
        pc_animation = True
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '2,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '2,0,1'
        coords = [int(i) for i in cell.split(',')]
        points = 12
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(len(scoreboard.history), 6)
        self.assertEqual(scoreboard.history[-1].get('points'), points)
        self.assertEqual(scoreboard.history[-2].get('points'), 1)
        scoreboard.save_points_changes()
        self.assertEqual(len(scoreboard.history), 5)
        self.assertIsNone(scoreboard.history[-1].get('points'))
        self.assertEqual(scoreboard.history[-1].get('scores'), [12, 0, 0, 0, 1])
        self.assertEqual(scoreboard.history[-1].get('round_num'), coords[0])
        self.assertEqual(scoreboard.history[-1].get('question_num'), 2)
        self.assertEqual(scoreboard.history[-2].get('points'), -30)
        self.assertEqual(scoreboard.history[-2].get('round_num'), 3)
        scoreboard.save()

        scoreboard = self.get_scoreboard()
        cell = '3,0,2'
        coords = [int(i) for i in cell.split(',')]
        points = -30
        pc_animation = True
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '3,0,5'
        coords = [int(i) for i in cell.split(',')]
        points = 1
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        cell = '3,0,1'
        coords = [int(i) for i in cell.split(',')]
        points = 12
        pc_animation = False
        gl_animation = True
        scoreboard.points_change(cell, points, pc_animation, gl_animation)
        self.assertEqual(len(scoreboard.history), 8)
        self.assertEqual(scoreboard.history[-1].get('points'), points)
        self.assertEqual(scoreboard.history[-2].get('points'), 1)
        scoreboard.save_points_changes()
        self.assertEqual(len(scoreboard.history), 6)
        self.assertIsNone(scoreboard.history[-1].get('points'))
        self.assertEqual(scoreboard.history[-1].get('scores'), [12, -30, 0, 0, 1])
        self.assertEqual(scoreboard.history[-1].get('round_num'), coords[0])
        self.assertEqual(scoreboard.history[-1].get('question_num'), 1)
        self.assertEqual(scoreboard.history[-3].get('points'), -30)
        self.assertEqual(scoreboard.history[-3].get('round_num'), 3)
        scoreboard.save()