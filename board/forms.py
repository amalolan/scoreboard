from django import forms
from .models import Scoreboard


class PositiveIntegerField(forms.IntegerField):
    """
    Enforces rule that num_rounds and num teams must be between 0 and 10.
    """
    def validate(self, value):
        super(PositiveIntegerField, self).validate(value)
        if value <= 0 or value >= 10:
            raise forms.ValidationError("Num Teams and Num Rounds must be " +
                                        "between 0 and 10.")


class ScoreboardCreateForm(forms.ModelForm):
    class Meta:
        model = Scoreboard
        fields = ['title', 'num_teams', 'num_rounds']
        field_classes = {
            'num_rounds': PositiveIntegerField,
            'num_teams': PositiveIntegerField
        }
