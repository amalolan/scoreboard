// Table animations
// TODO: Documentation. Improve code quality.
$('.round').click(function () {
  let animationSpeed = 'fast';
  onClick(this, animationSpeed);
});

function onClick(obj, animationSpeed) {
  animationSpeed = animationSpeed || 'fast';
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
      'padding-left': '0.9em',
      'padding-top': '0.9em',
      'padding-bottom': '0.9em',
      'overflow': 'hidden'
    }, {
      duration: animationSpeed,
      queue: false
    });
    $(self).nextUntil('tr.round').find('td:first-child').animate({
      'padding-left': '2em'
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
        'padding': '0px'
      }, {
        duration: animationSpeed,
        queue: true
      });
    }
  }
}

// Notification Animations
function notify(text, bg, fg, retractAfter, animationSpeed) {
  /**
   Pulls out a notification and then closes it after retractAfter ms.
   Inputs: text: String: A <p> tag with id textID. This will be displayed in the notification.
   bg: String: the ID of the background-box for notification
   fg: Sting: the ID of the foreground-box
   retractAfter: Number: no.of ms to wait before closing notification
   animationSpeed(OPTIONAL): String or Number
   */
  $(".round:not(.collapsed)").click();
  $("#temp-text").append(text);
  let temp_text_p = '#temp-text>p';
  let width = $(temp_text_p).width() + 50;
  $(temp_text_p).remove();
  $(bg).animate({
    'width': width
  }, {
    duration: animationSpeed,
    complete: function () {
      setTimeout(function () {
        $(bg).append(text);
        $(fg).animate({
          'width': width
        }, {
          duration: animationSpeed,
          complete: retract
        });
      }, 300);
    }
  });

  function retract() {
    /**
     Retracts the notification
     */
    setTimeout(function () {
      $(fg).animate({
        'width': 0
      }, {
        duration: animationSpeed,
        complete: function () {
          $(bg).find('p').remove();
          $(bg).animate({
            'width': 0
          }, {
            duration: animationSpeed
          });
        }
      });
    }, retractAfter);
  }

}

function notifyPlus(text, extraClass, retractAfter, animationSpeed) {
  /**
   Calls notify() after adding an extraClass to the notification box. This is
   used to display notifications of different styles.
   Inputs: text: String: The text to display in the notification
   extraClass: String The class to add to the notification box
   retractAfter: Number: no.of ms to wait before closing notification
   animationSpeed(OPTIONAL): NUMBER ONLY

   */
  animationSpeed = animationSpeed || 1000;
  let bg = "#notify-bg-box"; // NOTE: HARD-CODED
  let fg = "#notify-fg-box";
  $(bg).add(fg).add('#temp-text').addClass(extraClass);
  notify(text, bg, fg, retractAfter, animationSpeed);
  setTimeout(function () {
    $(bg).add(fg).add('#temp-text').removeClass(extraClass);
  }, retractAfter + (4 * animationSpeed + 500));
}

function winAnimation(team, retractAfter, animationSpeed) {
  /**
   Displays a win animation when a team is declared a winner
   Input: team: String: the team that won
   */
  retractAfter = retractAfter || 3000;
  let winner = team || "TEAM MALOLAN";
  let text = '<p id="notify-text">And the winner is......... <strong>' + winner + '.</strong></p>';
  notifyPlus(text, 'winner', retractAfter, animationSpeed);
}

function gainAnimation(score, team, retractAfter, animationSpeed) {
  /**
   Displays a gain notification when a team gains points
   Inputs: score: Number: the points gained
   team: String: the team that gained the points
   retractAfter: Number: the no.of ms to wait before closing the animation
   animationSpeed(OPTIONAL): String or Number
   */
  retractAfter = retractAfter || 3000;
  team = team || "Team Malolan";
  score = score || 10;
  let text = '<p id="notify-text">' + team + ' gained ' + score + ' points.</p>';
  notifyPlus(text, 'gain', retractAfter, animationSpeed);
}

function lossAnimation(score, team, retractAfter, animationSpeed) {
  /**
   Displays a loss notification when a team losses points
   Inputs: score: Number: the points lost
   team: String: the team that lost the points
   */
  retractAfter = retractAfter || 3000;
  team = team || "Team Malolan";
  score = score || 10;
  let text = '<p id="notify-text">' + team + ' lost ' + score + ' points.</p>';
  notifyPlus(text, 'loss', retractAfter, animationSpeed);
}

function changeCellClass(cell, currVal, amount, animationSpeed) {
  let cls = '';
  if ((currVal + amount) > 0) cls = 'positive';
  else if ((currVal + amount) < 0) cls = 'negative';
  let options = {
    duration: animationSpeed,
    easing: 'easeInQuad',
    queue: false
  };
  $(cell).removeClass('positive negative', options).addClass(cls,options);
}

// Number Increment Animations
function changeCellsValue(cells, amounts, animationSpeed) {
  /**
   Changes the amount in that cell along with an animation
   Inputs: cell: A jquery object/selector
   amount: the amount to change the cell by
   animationSpeed(OPTIONAL)
   */
  animationSpeed = animationSpeed || 'slow';
  for (let i = 0; i < cells.length; i++) {
    let cell = cells[i];
    let amount = amounts[i];
    let currVal = parseInt($(cell).html());
    changeCellClass(cell, currVal, amount, animationSpeed);
    $(cell)
        .prop('number', currVal)
        .animateNumber({
              number: currVal + amount,
              easing: 'easeInQuad',
              queue: false
            },
            animationSpeed);
  }
}

function makeExtras(cells, amounts, animationSpeed) {
  /**
   Shows the amount next to the cell before merging the two.
   Inputs: cell: A jquery object/selector
   amount: the amount to change the cell by
   animationSpeed(OPTIONAL): String or Number
   */
  animationSpeed = animationSpeed || 'medium';
  for (let i = 0; i < amounts.length; i++) {
    let amount = amounts[i];
    let cell = cells[i];
    let extraVal = (amount > 0 ? "+" : "");
    let className = (amount > 0 ? "positive" : "negative");
    extraVal += amount;
    let extra = '<span class="extra ' + className + '" style="display: none">' + extraVal + '</span>';
    $(cell).append(extra);
  }
  $('.extra').fadeIn(animationSpeed);
}

function moveExtras(animationSpeed) {
  /**
   Moves the extra cell towards the td and fades it away as it Moves
   Input: animationSpeed(OPTIONAL): String or Number
   */
  let extras = '.extra';
  $(extras).animate({
    'margin-left': '0.1em',
  }, {
    duration: animationSpeed,
    queue: false
  });
  $(extras).fadeOut({
    duration: animationSpeed,
    queue: false
  });
  setTimeout(function () {
    $(extras).remove();
  }, animationSpeed);
}

function changeCells(cells, amounts, waitTime, animationSpeed) {
  /**
   TODO: Test changeCells()
   Handles all animations to be done when a cell's amount needs to be changed;
   Inputs: cells: An array of jquery object/selector
   amounts: Array of Numbers: the amount to change each cell by
   animationSpeed(OPTIONAL): NUMBER ONLY
   waitTime(OPTIONAL): Number: the time to wait before fading out the
   extra cell.
   */
  $(".round:not(.collapsed)").click();
  animationSpeed = animationSpeed || 1500;
  waitTime = waitTime || 3500;
  makeExtras(cells, amounts);
  setTimeout(function () {
    moveExtras(animationSpeed);
    setTimeout(function () {
      changeCellsValue(cells, amounts);
    }, animationSpeed - 500);
  }, waitTime);
}

