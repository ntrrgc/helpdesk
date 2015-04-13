'use strict';

/* Angular JS configuration */

var app = angular.module('helpdesk', ['restangular', 'angularMoment', 'Snorky']);

app.config(function($httpProvider, RestangularProvider) {
   RestangularProvider.setBaseUrl(apiBaseUrl);
   RestangularProvider.setFullResponse(true);
   RestangularProvider.addFullRequestInterceptor(function
      (element, operation, path, url, headers, params, httpConfig) {
         // Insert CSRF token in non-GET requests
         if (-1 == _.indexOf(["get", "getList"], operation))
            headers['X-CSRFToken'] = csrfToken;

         return { headers: headers };
      });
});

var snorky;
var datasync;
var deltaProcessor;

app.run(function() {
   // Important: When using Angular-Snorky, all the initialization work
   // should be done in a .run() block.
   //
   // Otherwise Snorky will be already initialized before Angular-Snorky
   // module hooks event launching and promise classes.
   snorky = new Snorky(WebSocket, snorkyUrl, {
      'datasync': Snorky.DataSync
   }, {debug: true});
   datasync = snorky.services.datasync;

   deltaProcessor = new Snorky.DataSync.CollectionDeltaProcessor();

   datasync.deltaReceived.add(function(delta) {
      deltaProcessor.processDelta(delta);

      // Show desktop notifications (if the browser allows them)
      showNotificationMessage(delta);
   });
})

/* Controller (MVC) */

app.controller('AllIssuesCtrl', function($scope, Restangular) {
   window.scope = $scope
   $scope.formatAttention = function(attention) {
      return (attention ? "Needed" : "");
   };

   // This makes an AJAX call to GET /issues/ with an 'X-Snorky' header set to
   // Subscribe.
   $scope.issues = [];
   Restangular.all('issues').getList({}, {'X-Snorky': 'Subscribe'})
      .then(function(response) {
         // This function is called when the server replies

         // Assign the received data to issues model
         $scope.issues = response.data;

         // Tell the CollectionDeltaProcessor to process deltas over the
         // collection
         deltaProcessor.collections["Issue"] =
           new Snorky.DataSync.ArrayCollection($scope.issues);

         // Acquire the subscription with the token received
         var token = response.headers()['x-subscription-token'];
         datasync.acquireSubscription({token: token});
      });
});

app.controller('MyIssuesCtrl', function($scope, Restangular) {
   $scope.issues = [];
   Restangular.all('my-issues').getList({}, {'X-Snorky': 'Subscribe'})
      .then(function(response) {
         $scope.issues = response.data;
         deltaProcessor.collections["Issue"] =
             new ArrayCollection($scope.issues);
         var token = response.headers()['x-subscription-token'];
         datasync.acquireSubscription({token: token});
      });
});

var issueScope = null;
app.controller('IssueCtrl', function($scope, Restangular) {
   issueScope = $scope;
   $scope.replies = [];
   Restangular.one('issues', issueId).get({}, {'X-Snorky': 'Subscribe'})
      .then(function(response) {
         $scope.issue = response.data;
         $scope.replies = response.data.replies;

         // For single item updates
         deltaProcessor.collections["Issue"] =
            new Snorky.DataSync.SingleItemCollection(function() {
              return $scope.issue;
            }, function(newVal) {
               $scope.issue = newVal;
            });

         // For collection updates
         deltaProcessor.collections["IssueReply"] =
               new Snorky.DataSync.ArrayCollection($scope.replies);

         var token = response.headers()['x-subscription-token'];
         datasync.acquireSubscription({token: token});
      });

   $scope.replyForm = {
      issue: issueId,
      action: "none",
      content: ""
   };

   $scope.sending = false;
   $scope.send = function() {
      // Send form via AJAX
      $scope.sending = true;
      Restangular.all('replies').post($scope.replyForm)
         .then(function() {
            $scope.replyForm.content = "";
            $scope.replyForm.action = "none";
            $scope.sending = false;
         }, function() {
            alert("Sending failed");
            $scope.sending = false;
         });
   };
});

$(function() {
   if (typeof(Notification) !== "undefined" &&
      Notification.permission == "default")
   {
      var banner = $("#enable_notifications");
      banner.css("display", "inline-block");
      $("button", banner).click(function() {
         Notification.requestPermission(function() {
            banner.fadeOut("slow");
         });
      });
   }
});

function showNotificationMessage(delta) {
   if (typeof(Notification) === "undefined")
      return;

   if (viewName == "allIssues") {
      // Alert on new issues
      if (delta.model == 'Issue' && delta.type == 'insert') {
         var issue = delta.data;

         var title = "New issue from " + issue.initiator.first_name + " " +
            issue.initiator.last_name;
         var body = issue.title;

         new Notification(title, {body: body});
      }

      // Alert on existing issues that require attention
      if (delta.model == "Issue" && delta.type == 'update') {
         if (!delta.oldData.needs_attention &&
              delta.newData.needs_attention)
         {
            var title = "Issue requires attention";
            var body = delta.newData.title;

            new Notification(title, {body: body});
         }
      }
   } else if (viewName == "issue") {
      // Alert on replies, but not to the user that sends them
      if (delta.model == "IssueReply" &&
          delta.type == 'insert' &&
          delta.data.author.email != userEmail)
      {
         var title = issueScope.issue.title;
         var body = "A new reply has been received";

         new Notification(title, {body: body});
      }
   }
}
