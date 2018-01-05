// NOTE: Terrible quality code ahead, but it works. TODO: Fix CODE

let options = {
  'win_animation': {
    'retractAfter': 1000000,
    'animationSpeed': 1000
  },
  'gl_animation': {
    'retractAfter': 5000,
    'animationSpeed': 1000
  },
  'points_change': {
    'waitTime': 3500*3,
    'animationSpeed': 1000
  },
  'fix_overflow': {
    'animationSpeed': 1000
  }
};


function autoFixOverflow(cell, animationSpeed) {
  /**
   Marks a cell with padding-left as 1px and font-size as 0.9em
   Inputs: cell: A jquery object/selector
   animationSpeed(OPTIONAL): String or Number
   */
  animationSpeed = animationSpeed || 1000;
  $(cell).toggleClass('xl', animationSpeed);
}

function fixOverflow(cell, fontSize, paddingLeft, animationSpeed) {
  /**
   Fixes overflow in cell by adding certain styles to that cell.
   Inputs: cell: A jquery object/selector
   fontSize: String: The new font-size for that cell
   paddingLeft(OPTIONAL): Number: The new padding-left for that cell
   animationSpeed(OPTIONAL): String or Number
   */
  animationSpeed = animationSpeed || 1000;
  paddingLeft = paddingLeft || 'auto';
  $(cell).animate({
    'padding-left': paddingLeft,
    'fontSize': fontSize
  }, {
    duration: animationSpeed,
    queue: false
  });
}

function normalizeID(id) {
  return id.split(',').join('\\,');
}

function getTeam(id) {
  return $('#' + id).html()
}

function addQuestion(board, round_num) {
  let q_index = board[round_num].length - 1,
      q = board[round_num][q_index];
  let q_id = round_num + ',' + q_index;
  let html = '<tr class="question" id="' + q_id + '">';
  html += '<td class="name" style="padding: 0;">' + q[0] + '</td>';
  for (let i = 1; i < q.length; i++) {
    html += '<td style="padding: 0;">' + q[i] + '</td>';
  }
  html += '</tr>';
  let round_id = "#" + round_num + "\\,0";
  let question_id = "#" + normalizeID(q_id);
  $(round_id + " ~ .round:first").before(html);
  $(question_id)
      .find('td')
      .wrapInner('<div style="display: none;">')
      .parent()
      .find('td > div')
      .slideUp();
  $(round_id).removeClass('collapsed').addClass('collapsed');
}

function receiver(response) {
  animating=true;
  let scoreboard = response['scoreboard'],
      actions = response['actions'],
      animations = [];
  $.each(actions, function (i, action) {
    if (i === 'points_change') {
      let cells = [], vals = [];
      $.each(action, function (j, object) {
        cells.push('#' + normalizeID(object.cell));
        vals.push(object.points);
      });
      changeCells(cells, vals, options[i]['waitTime'], options[i]['animationSpeed']);
    } else if (i === 'fix_overflow') {
      autoFixOverflow('#' + action[0].cell, options[i]['animationSpeed'])
    } else if (i === 'win_animation') {
      winAnimation(getTeam(action[0].cell), options[i]['retractAfter'],
          options[i]['animationSpeed']);
      finished = true;
      return animating;
    } else if (i === 'add_question') {
      let round_num = action[0].cell.split(',')[0];
      addQuestion(scoreboard['board'], round_num);
    } else {
      for (let j = 0; j < action.length; j++) {
        let animation = {
          'points': action[j]['points'],
          'team': getTeam(action[j]['cell'])
        };
        animation['type'] = action[j]['animation_type'];
        animations.push(animation);
      }
    }
  });
  if (animations.length > 0) {
    let retractAfter = options['gl_animation']['retractAfter'],
        animationSpeed = options['gl_animation']['animationSpeed'],
        waitTime = retractAfter + 1000 + 4 * animationSpeed;
    animate();
    let interval = setInterval(animate, waitTime);
    function animate() {
      if (animations.length === 0) {
        clearInterval(interval);
        animating = false;
        return;
      }
      let animation = animations.pop();
      if (animation.type === 'gain') {
        gainAnimation(animation.points, animation.team, retractAfter,
            animationSpeed);
      } else {
        lossAnimation(-animation.points, animation.team, retractAfter,
            animationSpeed);
      }
    }
  } else animating = false;
}