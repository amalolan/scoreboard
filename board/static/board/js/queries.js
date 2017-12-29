/**
 * Queries are things sent from the manager page to the server giving it certain
 * instructions and telling it to do things to the scoreboard page.
 * For example, a points_query will tell the server to add x points to team y
 * in round z. This information, depending on the query, may be directly
 * sent to scoreboard, or make changes to the database and then get sent to
 * the scoreboard.
 *
 * These queries are sent via ajax POST requests. Each query is attached to a
 * form. When the form is submitted, the query is submitted. If this form has a
 * fixed id but needs to have different inputs shown there, then the query, once
 * submitted is deleted. Some queries also have input validation. These are only
 * submitted if the inputs are valid.
 */


/**
 * SimpleQuery Class
 * @class
 * @classdesc Query that doesn't need inp validation and submits via ajax
 * Sends a POST request {'choice': '', 'name': this.name}
 * 'choice' is always ''.
 * @example
 * win_animation
 */

class SimpleQuery {
  /**
   * Creates a SimpleQuery object
   * @constructor
   * @param {String} url - The url to call (currently, all urls are board:query)
   * @param {String} form - The form associated with this query, as a $ selector
   * @param {String} name - The name of that form/ name of this query
   */
  constructor(url, form, name) {
    this.url = url;
    this.form = form;
    this.name = name;
  }

  /**
   * Displays a success/failure msg in the msg box.
   * @param {String} msg - The msg to display
   * @param {Boolean} [success] - True if the msg is a success message.
   */
  static alertMsg(msg, success) {
    success = success || false;
    let msg_status = success ? 'SUCCESS' : 'ERROR';
    $('#msg-status').text(msg_status);
    $('#msg').text(msg);
    $('#msg, #msg-status').attr('class', msg_status.toLowerCase());
    $('body').css('cursor', 'default');
  }

  /**
   * On success of ajax call, send msg to alertMsg()
   * @param {String} response - Response from ajax call
   */
  success(response) {
    response = JSON.parse(response);
    SimpleQuery.alertMsg(response.msg, true);
  }

  /**
   * On failure of ajax call, send msg to alertMsg()
   * @param {String} response - Response from ajax call
   */
  error(response) {
    response = JSON.parse(response.responseText);
    SimpleQuery.alertMsg(response.msg);
  }

  /**
   * Submit's the form associated with the query by sending an ajax POST request
   * to this.url (board:query)..
   * Add's the form's name along with the serialized form. This serialized form
   * may include .choices which contains extra information which normally don't
   * get serialized.
   */
  submit() {
    let self = this;
    let data = $(this.form).serializeArray();
    data.push({name: 'name', value: $(this.form).attr('name')});
    $.ajax({
      data: data,
      type: $(this.form).attr('method'),
      url: this.url,
      success: function (response) {
        self.success(response);
      },
      error: function (response) {
        self.error(response);
      }
    });
  }
}

/**
 * Query Class
 * @extends SimpleQuery
 * @classdesc Query that has a choice field that might need inp validation.
 * Sends a POST request {'choice': theme, 'name': this.name}
 * For now, only set_theme is a Query. 'choice' can take on any one of 4 values.
 * @example
 * set_theme
 */

class Query extends SimpleQuery {
  /**
   * Validate's form inputs. If validation fails, displays error msg in msg box.
   * @returns {boolean} - true if validation passed, false otherwise
   */
  validate() {
    if ($(this.form).find('.choice').attr('value') === "") {
      Query.alertMsg("Please click on a table cell with a value before submitting");
      return false;
    }
    return true;
  }

  /**
   * Overrides super.submit by including validation. If validation fails,
   * it doesn't submit
   * @override
   */
  submit() {
    if (this.validate())
      super.submit();
  }
}

/**
 * ClickQuery Class
 * @class
 * @classdesc Query that needs validation and has a choice of team.
 * Sends a POST request of {'choice': cell, 'points': points, 'name': this.name}
 * where cell is a team name and points is the change in points for that team
 * which must be displayed as an animation.
 * @example
 * fix_overflow
 */

class ClickQuery extends Query {

  /**
   * At this stage, the super.validate() is saved as validateChoice().
   * This is useful for sub-classes which require access to super.validate()
   * but at the same time don't want the overridden .validate() from this class
   * Sends a POST request of {'choice': cell, 'name': this.name}, where cell is
   * a team name's cell with value team1, team2, ...
   * @returns {boolean} - true if validation passes, false otherwise
   */
  validateChoice() {
    return super.validate();
  }

  /**
   * Overrides super.validate() by including additional validation tests.
   * @override
   * @returns {boolean} - true if validation passes, false otherwise
   */
  validate() {
    if (super.validate() === false) return false;
    let choice = $(this.form).find('.choice').attr('value');
    if ($('#' + choice).prop("tagName") !== 'TH' || choice === 'rounds') {
      SimpleQuery.alertMsg("Please click on the team's name");
      return false;
    }
    return true;
  }
}

/**
 * GainLossQuery Class
 * @class
 * @classdesc Queries that need changing #input-form with just number inputs
 * Sends a POST request of {'choice': cell, 'name': this.name, 'points', points}
 * where cell is a team's name, and points is the points change for that team
 * @example
 * gain_animation
 */

class GainLossQuery extends ClickQuery {

  /**
   * Creates the number input boxes.
   * @returns {string} - HTML of input boxes to append onto #input-form.
   */
  createInputs() {
    let inp = '';
    inp += '<div><label>Click on table then, enter the change in points here:</label>';
    inp += '<input type="number" name="points" required class="non-zero"></div>';
    return inp;
  }

  /**
   * Removes any existing input boxes and other tags from #input-form.
   * Whenever the .action button corresponding to this query is clicked on,
   * it toggles the form's visibility.
   */
  clearForm() {
    $(this.form).find('.free').find(":not(input:hidden):not(input:submit)").remove();
    $(this.form).attr('name', '');
    $(this.form).attr('action', '');
    $(this.form).find('.on_make').toggle();
  }

  /**
   * Creates the form by adding the input boxes and form attributes from this.
   */
  makeForm() {
    this.clearForm();
    $(this.form).attr('name', this.name);
    $(this.form).attr('action', this.url);
    $(this.form).find('.free').prepend(this.createInputs());
  }

  /**
   * overrides SimpleQuery.success() by also clearing the form and deleting
   * this.
   * @override
   * @param response - Response from ajax call
   */
  success(response) {
    super.success(response);
    this.clearForm();
    delete this;
    console.log(this)
  }

  /**
   * overrides SimpleQuery.error() by also clearing the form and deleting
   * this.
   * @override
   * @param response - Response from ajax call
   */
  error(response) {
    super.error(response);
    this.clearForm();
    delete this;
    console.log(this)
  }
}

/**
 * PointsQuery Class
 * @class
 * @classdesc Query with #input-form with number and checkbox inputs.
 * Sends a POST request of {'choice': cell, 'name': this.name, 'points', points,
 *  pc_animation: True or no field, gl_animation: True or no field}
 * where cell is a team's name, points is the points change for that team,
 * pc_animation exists if an animation has to be included with the points change
 * and gl_animation exists if a gain_loss animation needs to be included.
 * @example
 * points_change
 */

class PointsQuery extends GainLossQuery {

  /**
   * Creates a PointsQuery instance
   * @constructor
   * @param {String} url - The url to call (currently, all urls are board:query)
   * @param {String} form - The form associated with this query, as a $ selector
   * @param {String} name - The name of that form/ name of this query
   * @param {String} qtype - action or animation
   */
  constructor(url, form, name, qtype) {
    super(url, form, name);
    this.qtype = qtype;
  }

  /**
   * Changes name to makeInputs() as createInputs() must contain the final
   * input (According to super.makeForm())
   * @returns {string} - Inputs made by super.createInputs();
   */
  makeInputs() {
    return super.createInputs();
  }

  /**
   * Including number inputs, it also requires checkbox inputs which convey
   * if animations are required along with the action.
   * @returns {string} - HTML of checkbox inputs
   */
  makeInputAnimations() {
    let inp = '';
    inp += '<div><label class="check-label">Include points change animation?</label>';
    inp += '<input type="checkbox" name="pc_animation" value="True"';
    if (this.qtype === 'animation') {
      inp += 'checked required';
    }
    inp += '></div>';
    inp += '<div><label class="check-label">Include gain/loss animation?</label>';
    inp += '<input type="checkbox" name="gl_animation" value="True"></div>';
    return inp
  }

  /**
   * Combines number & checkbox inputs into single string. This is passed onto
   * makeForm()
   * @override
   * @returns {string} - HTML of number & checkbox inputs
   */
  createInputs() {
    let inp = this.makeInputs();
    inp += this.makeInputAnimations();
    return inp;
  }

  /**
   * Validates inputs further. Call's validateChoice as it doesn't need super's
   * validate().
   * @override
   * @returns {boolean} - true if validation passes, false otherwise
   */
  validate() {
    if (this.validateChoice() === false) return false;
    let coords = ($(this.form).find('.choice').val()).split(','),
        cell = '#' + coords.join('\\,');
    // cell = #ID
    if (($(cell).prop('tagName') !== 'TD') || (coords[0] === '0') ||
        (coords[1] !== '0')) {
      SimpleQuery.alertMsg("Please click on a table cell that isn't in the " +
          "heading, total, or question row.");
      return false;
    }
    return true;
  }
}

/**
 * QuestionQuery Class
 * @class
 * @classdesc Query which needs no.of teams input boxes and checkbox inputs.
 * Sends a POST request of {'choice': cell, 'name': this.name,
 *  pc_animation: True or no field, gl_animation: True or no field,
 *  'team1': pc_for_team1, 'team2', pc_for_team2 .....}
 * where cell is a team's name, pc_animation exists if an animation has to be
 * included with the points change, gl_animation exists if a gain_loss animation
 * needs to be included, and finally team ids with points change for that team.
 * @example
 * add_question
 */

class QuestionQuery extends PointsQuery {
  /**
   * Overrides super.makeInputs() as it needs 4 boxes compared to 1.
   * Uses the same .makeAnimationInputs().
   * @override
   * @returns {string}
   */
  makeInputs() {
    let inp = '';
    inp += '<div><label>Click on the table. Then for each team\'s name, enter their change in points:</label></div><div>';
    let num_teams = $('.containerTable th').length - 1;
    for (let i = 0; i < num_teams; i++) {
      let id = 'team' + (i + 1);
      inp += '<label>' + $('#' + id).text() + ':</label>';
      inp += '<input type="number" name="' + id + '" required>';
    }
    inp += '</div>';
    return inp;
  }
}
