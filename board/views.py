from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse
from django.core.urlresolvers import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, View
from django.views.generic.edit import DeleteView
from .generic import QueryView
from .models import Scoreboard
from .forms import ScoreboardCreateForm


# TODO: Documentation for views.py

class HomeView(ListView):
    """Renders the homepage of the board app."""
    model = Scoreboard
    context_object_name = 'board_objects'
    template_name = 'board/home.html'


class ScoreboardCreate(CreateView):
    """Creates a new board."""
    model = Scoreboard
    form_class = ScoreboardCreateForm
    success_url = reverse_lazy('board:home')
    
    def form_valid(self, form):
        """
        Overrides CreateView.form_valid as it also saves the teams array
        and calls Scoreboard.new_board()
        """
        response = super(ScoreboardCreate, self).form_valid(form)
        # print(form.save())
        self.object.teams = self.teams
        self.object.new_board()
        self.object.save()
        return response
    
    def post(self, request, *args, **kwargs):
        self.teams = [request.POST['team' + str(i + 1)]
                      for i in range(int(request.POST['num_teams']))]
        return super(ScoreboardCreate, self).post(request, *args, **kwargs)


class ScoreboardView(DetailView):
    """
    Creates the scoreboard front end page and displays it to the user.
    """
    model = Scoreboard
    context_object_name = 'scoreboard'
    template_name = 'board/scoreboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scoreboard = get_object_or_404(Scoreboard,
                                       pk=self.kwargs.get('pk', None))
        context['board'] = scoreboard.board.copy()
        context['sum_row'] = context['board'].pop(0)[0]
        return context


class ManagerView(ScoreboardView):
    template_name = 'board/manager.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        scoreboard = get_object_or_404(Scoreboard,
                                       pk=self.kwargs.get('pk', None))
        context['history'] = []
        for i in scoreboard.history:
            if not i.get('points'):
                j = [i.get('round_num'), str(i.get('scores')),
                     i.get('question_num')]
                obj_type = 'question'
            else:
                obj_type = 'points'
                j = [i.get('round_num'), i.get('points'),
                     i.get('team_num')]
            context['history'].append((obj_type, j))
        return context


class GetChanges(View):
    """
    Every few seconds, a get request is made from board:scoreboard.
    If no changes were made, returns nothing, else returns the changes made.
    """
    model = Scoreboard
    
    def get(self, request, pk):
        """:return JsonResponse of the Board instance."""
        data = {}
        scoreboard = get_object_or_404(self.model, pk=pk)
        if scoreboard.is_changed():
            data = scoreboard.get_dict()
            scoreboard.sent()
        return JsonResponse(data)


class ScoreboardDelete(DeleteView):
    """Deletes all Scoreboards if pk=0, else just that object"""
    model = Scoreboard
    success_url = reverse_lazy('board:home')
    
    def delete(self, request, *args, **kwargs):
        if self.kwargs.get('pk', None) == '0':
            self.model.objects.all().delete()
            return HttpResponseRedirect(self.success_url)
        return super().delete(request, *args, **kwargs)


class ThemeQuery(QueryView):
    def get_success_msg(self, request, result):
        return "Successfully changed Scoreboard's theme to '" + result + "'."
    
    def post_handler(self, request, model_instance):
        return model_instance.set_theme(request.POST['choice'])


class OverflowQuery(QueryView):
    def get_success_msg(self, request, result):
        return ("Successfully toggled heading overflow of Team " +
                result[4:] + ".")  # 'choice' = 'team[0-9]+'
    
    def post_handler(self, request, model_instance):
        return model_instance.fix_overflow(request.POST['choice'])


class WinQuery(QueryView):
    def get_success_msg(self, request, result):
        return "Successfully declared Team " + result + " as the winner."
    
    def post_handler(self, request, model_instance):
        return model_instance.win_animation()


class GainLossQuery(QueryView):
    def get_success_msg(self, request, result):
        return ("Successfully performed a " +
                result['type'] + " animation " + "for Team " +
                result['team'][4:] + " with " +
                str(result['points']) + " points.")
    
    def post_handler(self, request, model_instance):
        return model_instance.gain_loss_animation(
            request.POST['choice'], int(request.POST['points']))


class PointsChangeQuery(QueryView):
    def get_success_msg(self, request, result):
        return ("Successfully added " +
                str(result['points']) + " points to Team " +
                result['team'][4:] + " in Round " +
                str(result['round']) + " .")
    
    def post_handler(self, request, model_instance):
        gl_animation, pc_animation = False, False
        if request.POST.get("gl_animation"):
            gl_animation = True
        if request.POST.get("pc_animation"):
            pc_animation = True
        coords = request.POST['choice']
        points = int(request.POST['points'])
        return model_instance.points_change(coords, points, pc_animation,
                                            gl_animation)


class QuestionQuery(QueryView):
    def get_success_msg(self, request, result):
        return ("Successfully added Question " +
                str(result['question_no']) + " to Round " +
                str(result['round_no']) + " with points for teams as " +
                str(result['scores']) + ".")
    
    def post_handler(self, request, model_instance):
        round_num = int(request.POST['choice'].split(',')[0])
        gl_animation, pc_animation = False, False
        if request.POST.get("gl_animation"):
            gl_animation = True
        if request.POST.get("pc_animation"):
            pc_animation = True
        num_teams = model_instance.num_teams
        scores = []
        for i in range(1, num_teams + 1):
            scores.append(int(request.POST['team' + str(i)]))
        return model_instance.question(round_num, scores, pc_animation,
                                       gl_animation)


class SavePointsQuery(QueryView):
    def get_success_msg(self, request, result):
        return ("Successfully saved points changes to Question " +
                str(result['question_no']) + " in Round " +
                str(result['round_no']) + " with " + " points for teams as " +
                str(result['scores']) + '.')
    
    def post_handler(self, request, model_instance):
        return model_instance.save_points_changes()


class UndoQuery(QueryView):
    def get_success_msg(self, request, result):
        return "Successfully removed latest" + result['obj_type'] + "."
    
    def post_handler(self, request, model_instance):
        return model_instance.undo()


class RecalculateQuery(QueryView):
    def get_success_msg(self, request, result):
        return "Successfully recalculated the board's points."
    
    def post_handler(self, request, model_instance):
        return model_instance.calculate()
