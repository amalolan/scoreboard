// Table animations
$('.round > .name').click(function () {
  onClickRound($(this).parent());
});

function onClickRound(obj) {
  let animationSpeed = 'fast';
  let self = obj;
  if ($(self).hasClass("collapsed")) {
    $(self).nextUntil('tr.round')
        .find('td')
        .parent()
        .find('td > div')
        .slideDown("fast", function () {
          let $set = $(this);
          $set.replaceWith($set.contents());
        });
    $(self).removeClass("collapsed");
    $(self).nextUntil('tr.round').find('td').animate({
      'padding-left': '1%',
      'padding-top': '1%',
      'padding-bottom': '1%',
      'overflow': 'hidden'
    }, {
      duration: animationSpeed,
      queue: false
    });
    $(self).nextUntil('tr.round').find('td:first-child').animate({
      'padding-left': '2%'
    }, {
      duration: animationSpeed,
      queue: true
    });
  } else {
    $(self).nextUntil('tr.round')
        .find('td')
        .wrapInner('<div style="display: block;" />')
        .parent()
        .find('td > div')
        .slideUp("fast");
    if ($(self).next().hasClass("question")) {
      $(self).addClass("collapsed");
      $(self).nextUntil('tr.round').find('td').animate({
        padding: '0px'
      }, {
        duration: animationSpeed
      });
    }
  }
}

$(document).ready(function () {
  /**
   * th, td on click, assigns it's id to the global variable chosen which
   * is used by the Queries to find out where the user clicked on the table.
   */
  $("th, td").not('.name').click(function () {
    chosen = this.id;
  });

  /**
   *  Asks for confirmation of deletion of the board.
   */
  $('.del').click(function () {
    $('.del').toggle();
  });

  /**
   * Asks for confirmation of a click. Used for win, delete, and undo.
   */
  $('.confirm').click(function() {
    $(this).toggle().siblings('.confirm').toggle();
  });
  /**
   * On any button click, chosen is reset and all open rounds are collapsed.
   */
  $('button').click(function () {
    chosen = '';
    $(".round:not(.collapsed)").find(".name").click();
  });

  /**
   * If a submit button in .choose is pressed (set_theme form), then the name
   * of the button that is pressed is saved in the hidden input .choice. This
   * helps in passing this choice onto views as the form is serialized with
   * .choice and its value.
   */
  $('.choose input[type=submit]').click(function () {
    $(this).parent().find('.choice').attr('value', $(this).attr('name'));
    $('body').css('cursor', 'wait');
  });

  /**
   * In many other forms, the user has to click on a table cell. Once clicked,
   * that cell's ID is stored in chosen. When the user submits the form, the
   * hidden input .choice takes in chosen's value. This way, chosen's value is
   * passed onto views.
   */
  $('.table-choose input[type=submit]').on('click', function () {
    $(this).closest('.table-choose').find('.choice').attr('value', chosen);
    chosen = '';
    $('body').css('cursor', 'wait');
  });

  /**
   * On the click of any form that doesn't require a page refresh, the submit
   * function of the query instance corresponding to that form is called.
   * All queries and their respective form names are stored in the global
   * queries object.
   */
  $('form').not('.refresh').submit(function (e) {
    e.preventDefault();
    queries[$(this).attr('name')].submit();
    return false;
  });

  /**
   * Makes sure numerical inputs are non zero instead of validating in queries
   */
  $(document).on("keyup", ".non-zero", function () {
    if ($(this).val() === '0') {
      $(this).val(null);
    }
  });

  /**
   * Action/Animation buttons
   * On the click of any of these buttons, their respective queries are created.
   * These also toggle the visibility of the #input-form.
   */
  $(".action, .animation").click(function () {
    let queryChoices = {
          'points_change': PointsQuery,
          'points_change_animation': PointsQuery,
          'add_question': QuestionQuery,
          'gain_animation': GainLossQuery,
          'loss_animation': GainLossQuery
        },
        id = $(this).attr('id'),
        cls = $(this).attr('class');
    if (queries[id]) {
      let form = "#input-form";
      queries[id].clearForm();
      $(form).find('.on_make').hide();
      queries[id] = null;
    }
    else {
      let query = new queryChoices[id](urls[id], '#input-form',
          id, cls); // url, form, name, qtype
      queries[id] = query;
      query.makeForm();
    }
  });
});
