from django.db import models
from django.forms.models import model_to_dict
from picklefield.fields import PickledObjectField
from polymorphic.models import PolymorphicModel


# TODO: Documentation for models.py

class Scoreboard(models.Model):
    """
    This is the scoreboard model. It contains the board, the questions' history,
    and temporary bools as foreign keys. Temp bools indicate if any change
    has been made or have to be made for the scoreboard page.
    """
    title = models.CharField(max_length=100, default="Scoreboard")
    theme = models.CharField(max_length=20, default="default")
    num_teams = models.IntegerField(default=0)
    num_rounds = models.IntegerField(default=0)
    teams = PickledObjectField(default=[])
    board = PickledObjectField(default=[])
    history = PickledObjectField(default=[])
    changed = models.BooleanField(default=False)
    
    def new_board(self):
        """
        Creates a new board by filling the data cells with 0 and gives the
        rounds their appropriate names(TOTAL, Round 1, Round 2, etc.)
        :return: self.board
        """
        b = [] * (self.num_rounds + 1)
        for i in range(self.num_rounds + 1):
            x = [['Round ' + str(i)] + [0] * self.num_teams]
            b.append(x[:])
        b[0][0][0] = 'TOTAL'
        self.board = b
        return self.board
    
    def set_title(self, title):
        """
        :param str title: H1 of scoreboard.html
        :return: None
        """
        self.title = title
    
    def set_theme(self, theme):
        """
        Sets self.theme to the chosen theme. big-bold is toggled on and off
        :param str theme: The board:scoreboard theme: light-blue, light-brown
        :return str: The updated theme
        """
        if 'big-bold' in self.theme:
            if theme == 'big-bold':
                self.theme = self.theme.replace('big-bold', '')
                self.theme = self.theme.replace(' ', '')
            else:
                self.theme = theme + ' big-bold'
        else:
            if theme == 'big-bold':
                self.theme += " big-bold"
            else:
                self.theme = theme
        return self.theme
    
    def fix_overflow(self, team):
        """
        Saves an action to fix_overflow of the team. This is later sent to
        board:scoreboard via the get request it makes every few seconds.
        :param str team: The teamID to fix_overflow for.
        :return str: The fix_overflow team
        """
        if not self.action_set.filter(name="fix_overflow", cell=team).count():
            Action.objects.create(name="fix_overflow", cell=team,
                                  scoreboard=self)
        return team
    
    def win_animation(self):
        """
        Creates an action for a win_animation.
        :return str: The winning team
        """
        winner = self.get_winner()
        Action.objects.create(name="win_animation", cell=winner,
                              scoreboard=self)
        return winner
    
    def gain_loss_animation(self, team, points):
        """
        Creates a gain/loss animation action object which will be passed on to
        board:scoreboard
        :param str team: team[0-9]+
        :param int points: Points change for that team
        :return dict: {'team': team, 'points': points, 'type': 'gain' or 'loss'}
        """
        assert points != 0, "Points can't be 0"
        animation_type = "gain"
        if points < 0:
            animation_type = "loss"
        GainLossAction.objects.create(name="gain_loss_animation", cell=team,
                                      scoreboard=self, points=points,
                                      animation_type=animation_type)
        return {'team': team, 'points': points, 'type': animation_type}
    
    def points_change(self, coords, points, pc_animation, gl_animation):
        """
        Creates a points_change action object. Also creates gain/loss object
        if gl_animation is True. Also changes the points of cell at coords.
        :param [int] coords: List of integers of length 3 containing the coords
        :param int points:Points change for that team
        :param bool pc_animation: True of pc_animation should be performed
        :param bool gl_animation: True if gl_animation should be performed
        :return: {'points': points, 'team': team for which points were changed,
                  'round': round for which points were changed'}
        """
        assert points != 0, "Points can't be 0"
        if pc_animation:
            animation_type = "gain"
            if points < 0:
                animation_type = "loss"
        else:
            animation_type = 'null'
        ptc = PointsChangeAction.objects.create(
            name="points_change", points=points, animation_type=animation_type,
            cell=coords, gl_animation=gl_animation, scoreboard=self)
        ptc.add_animations()
        coords = [int(i) for i in coords.split(',')]
        self.change_points([coords], [points])
        print(coords[0])
        self.history.append({'points': points, 'round_num': coords[0],
                             'team_num': coords[2]})
        return {'points': points, 'team': 'team' + str(coords[2]),
                'round': str(coords[0])}
    
    def question(self, round_num, scores, pc_animation, gl_animation):
        animation_type = 'gain'
        cell = str(round_num) + ',0'
        if not pc_animation:
            animation_type = 'null'
        question_action = QuestionAction.objects.create(
            name="add_question", cell=cell, points=1, gl_animation=gl_animation,
            animation_type=animation_type, scores=scores[:], scoreboard=self)
        question_action.add_animations()
        question = self.add_question(round_num, scores)
        self.calculate()
        self.history.append({'scores': scores, 'round_num': round_num,
                             'question_num': int(question[0][9:])})
        return {'question_no': question[0][9:], 'round_no': round_num,
                'scores': scores}
    
    def save_points_changes(self):
        assert self.history != [], "History is empty!"
        pcs = []
        round_num = 0
        for i in range(len(self.history) - 1, -1, -1):
            if self.history[i].get('points'):
                curr_round_num = int(self.history[i].get('round_num'))
                if not round_num:
                    round_num = curr_round_num
                if round_num == curr_round_num:
                    pcs.append(self.history.pop(i))
            else:
                break
        assert round_num != 0, "No points changes recorded."
        scores = [0] * self.num_teams
        for i in pcs:
            scores[int(i['team_num']) - 1] += int(i['points'])
        return self.question(round_num, scores, False, False)
    
    def undo(self):
        assert self.history != [], "History is empty!"
        latest = self.history.pop()
        if not latest.get('points'):
            round_num = int(latest['round_num'])
            question_num = int(latest['question_num'])
            self.board[round_num].pop(question_num)
            self.calculate()
            return {'obj_type': 'Question'}
        return {'obj_type': 'Points Change'}
    
    def calculate(self):
        """
        TODO: test models.Scoreboard.calculate()
        :return list: The Sum Row [Total of scores of all teams]
        """
        for i in range(self.num_rounds, -1, -1):
            self.get_sum(i)
        return self.board[0][0]
    
    def get_sum(self, round_num=0):
        """
        TODO: test models.board.get_sum()
        Gets the total sum of all rounds if round_num = 0 for each team.
        Else, it gets the total sum of scores of each question in that round,
        for each team.
        :param int round_num: The round to set the sum of questions' scores for.
               If round-num = 0, it gets the sum for the whole table.
        :return: list: The calculated row (1D)
        """
        assert self.board != [], "Please create self.board first. Run " \
                                 "self.new_board()"
        assert 0 <= round_num <= self.num_rounds, "Please enter a valid round"
        
        self.board[round_num][0] = [self.board[round_num][0][0]] + \
                                   [0] * self.num_teams
        if round_num == 0:
            for i in range(1, self.num_rounds + 1):
                for j in range(1, self.num_teams + 1):
                    self.board[0][0][j] += self.board[i][0][j]
            return self.board[0][0]
        else:
            for i in range(1, len(self.board[round_num])):
                for j in range(1, self.num_teams + 1):
                    self.board[round_num][0][j] += self.board[round_num][i][j]
            return self.board[round_num][0]
    
    def get_winner(self):
        """
        Gets the team with the most scores.
        :return str: the winning team: team[0-9]+
        """
        self.calculate()
        maximum = 0
        maximum_i = 0
        total = self.board[0][0]
        for i in range(1, len(total)):
            if 0 < total[i] == maximum:
                raise AssertionError("Two or more teams have the same scores. "
                                     "Can't declare a winner.")
            if total[i] > maximum:
                maximum = total[i]
                maximum_i = i
        assert maximum != 0, "No team has scored more than 0."
        return 'team' + str(maximum_i)
    
    def change_points(self, coords_list, points_list):
        assert len(coords_list) == len(points_list), "Tne lists have diff lens."
        for i in range(len(coords_list)):
            coords, points = coords_list[i], points_list[i]
            self.board[coords[0]][0][coords[2]] += points
            self.board[0][0][coords[2]] += points
    
    def add_question(self, round_num, scores):
        """
        Add's a question to the round round_num.
        :param int round_num: > 1. The round's index
        :param list scores: The points for each team (int list) in that question
        :return list: The question added (1D)
        """
        assert len(scores) == self.num_teams, "Enter scores exactly for all " \
                                              "the teams."
        assert self.board != [], "Please create self.board first. Run " \
                                 "self.new_board()"
        assert 0 < round_num <= self.num_rounds, "Please enter a valid round"
        question = ["Question " + str(len(self.board[round_num]))] + \
                   [int(i) for i in scores]
        self.board[round_num].append(question)
        return question
    
    def is_changed(self):
        """
        'Changed': The board is changed if and only if any data other than
                   TBs are changed.
        :return: bool: True if board is 'changed', False otherwise
        """
        return self.changed
    
    def sent(self):
        """
        Called after ajax get request from scoreboard is completed.
        Removes all previous TBs and adds a new changed TB indicating that
        both the scoreboard and db are in sync.
        :return:  None
        """
        self.changed = False
        for i in self.action_set.all():
            i.delete_self()
        self.save(override=True)
    
    def delete(self, using=None, keep_parents=False):
        for i in self.action_set.all():
            i.delete_self()
        super(Scoreboard, self).delete(using=using, keep_parents=keep_parents)
    
    def save(self, override=False, *args, **kwargs):
        """
        Called when changes are made to model and need to be saved to the db.
        When a change is made, it sets tempbool changed to True indicating that
        the scoreboard and db are not in sync and need to be synced.
        :return: None
        """
        if not override:
            self.changed = True
        super(Scoreboard, self).save(*args, **kwargs)
    
    def get_dict(self):
        """
        Converts self into dict/json and tempbools into dicts grouped by their
        type.
        :return: json: of self and tempbools arranged by type
        """
        base = model_to_dict(self)
        base['board'] = self.board
        base['teams'] = self.teams
        actions_list = [model_to_dict(i) for i in self.action_set.all()]
        actions = {}
        for i in actions_list:
            if actions.get(i['name']) is None:
                actions[i['name']] = []
            actions[i['name']].append(i)
        return {'scoreboard': base, 'actions': actions}
    
    def __str__(self):
        string = str(self.id) + ", " + self.title
        # string += '\n'
        # string += self.board.__str__()
        return string


class Action(PolymorphicModel):
    name = models.CharField(max_length=100)
    cell = models.CharField(max_length=20)
    scoreboard = models.ForeignKey(Scoreboard)
    
    def delete_self(self):
        self.delete()


class GainLossAction(Action):
    points = models.IntegerField(default=0)
    GAIN, LOSS, NULL = 'gain', 'loss', 'null'
    CHOICES = ((GAIN, 'gain'), (LOSS, 'loss'), (NULL, 'null'))
    animation_type = models.CharField(max_length=5, choices=CHOICES)


class PointsChangeAction(GainLossAction):
    gl_animation = models.BooleanField(default=False)
    
    def add_animations(self):
        if self.gl_animation:
            team = 'team' + self.cell.split(',')[2]
            a_type = 'gain'
            if self.points < 0:
                a_type = 'loss'
            GainLossAction.objects.create(
                name="gain_loss_animation", points=self.points, cell=team,
                scoreboard=self.scoreboard, animation_type=a_type)
        if self.animation_type == 'null':
            self.delete()


class QuestionAction(PointsChangeAction):
    scores = PickledObjectField(default=[])
    
    def add_animations(self):
        """
        TODO: Increase code quality
        :return:
        """
        if self.gl_animation is False and self.animation_type == 'null':
            return
        for i in range(1, len(self.scores) + 1):
            cell = self.cell + "," + str(i)
            cell2 = '0,0,' + str(i)
            points = self.scores[i - 1]
            if points == 0:
                continue
            if self.animation_type == 'null':
                a_type = 'null'
            elif points < 0:
                a_type = 'loss'
            else:
                a_type = 'gain'
            pc = PointsChangeAction.objects.create(
                name="points_change", points=points, animation_type=a_type,
                cell=cell, gl_animation=self.gl_animation,
                scoreboard=self.scoreboard
            )
            pc.add_animations()
            if a_type != 'null':
                pc2 = PointsChangeAction.objects.create(
                    name="points_change", points=points, animation_type=a_type,
                    cell=cell2, gl_animation=False, scoreboard=self.scoreboard)
                pc2.add_animations()
