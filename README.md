# Scoreboard

This is a scoreboard web app which can be used for any quiz. It comes with a self-updating front-end view as well as a back-end manager view. Since this scoreboard was initially built for my school's annual quiz competition which would host not more than 10 teams, the maximum number of teams and rounds has been limited to 10\. The app is live on [heroku.](https://quiz-scoreboard.herokuapp.com/)

## How it works

-   The front-end page currently works by sending a GET request to the server every 4 seconds. This is **NOT THE OPTIMAL method** to use if there are more than a few users at a time as this would cause extreme server stress. A better option would be to use some sort of a [COMET](https://en.wikipedia.org/wiki/Comet_(programming)) approach.

-   Once a form is submitted on the manager page, the server receives that submission, performs actions on the server if necessary, and queues up the animations and actions for the front-end page to execute.

-   Once the next GET request is received, all these queued actions are sent to the front-end to execute.

-   Once the execution of the actions/animations has been completed, the front-end resumes sending the GET requests.

## Possible Optimizations

1.  ##### Using COMET instead of repeated GET requests.

2.  ##### Reducing the number of model classes all linked by inheritance.

    Each one of these classes causes an extra overhead on the database and adds additional joins. This is the reason why adding a question with all animations takes a few seconds (up to 3 seconds for just 5-7 teams) and thus is also the reason why the front end only polls every 4 seconds and not more frequently. Reducing the joins could drastically reduce the time taken for operations.

3.  ##### Using postgresql's JSON fields instead of Pickled-object fields to store the serialized board and history objects.

    Using a JSON field directly in postgresql instead of using a pickled field **might** reduce operation times.

## Possible design change

Handling what is sent to the front-end by the server is probably not the optimal way to do it for a few reasons. Once the GET request is recieved and data is sent over, those queued actions are immediately deleted on the server. This means that two front-end scoreboards cannot simultaneously receive animations for that Quiz instance. A better approach would be to always receive the complete list of actions and decide what to do on the client(front-end) side instead of making those decisions on the server side. This would let more than one client side connection exist at a time, but, on the other hand, would increase the size of the response and would require more complex logic on the client side: the reason I chose to do it server-side.

## Examples
Here are a few examples of this scoreboard running.
![](image1.png)
When a team wins:
![](image2.png)
The front-end view:
![](image3.png)
The manager view:
![](image4.png)

## Credits

Alexandr Borisov for [jQuery-animateNumber](https://github.com/aishek/jquery-animateNumber), licensed under the [MIT license.](https://github.com/aishek/jquery-animateNumber/blob/master/LICENSE)

## License

The software is free, and may be redistributed under the terms specified in the [LICENSE file.](https://github.com/amalolan/scoreboard/blob/master/LICENSE)
