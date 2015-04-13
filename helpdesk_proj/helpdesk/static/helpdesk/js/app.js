'use strict';

/* Angular JS configuration */

var app = angular.module('helpdesk', ['restangular', 'angularMoment']);

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

// Delta processor: A class that receives deltas from the connector and
// processes them. Will be configured later.
//
// The class hierarchy is something like this:
//
// +------------------+
// |  <<Interface>>   |  DeltaProcessor is just an interface for an object
// |  DeltaProcessor  |  which receives deltas and processes them the way it
// +------------------+  likes.
// | +onDelta(delta)  |
// +--------.---------+
//         /_\
//          |
// +--------+-----------------+
// | CollectionDeltaProcessor |  CollectionDeltaProcessor maintains a set of
// +--------------------------+  collections identifying each one with a model
// | +onDelta(delta)          |  class name (as used in delta items) and
// +-.---------O--------------+  updates them when deltas arrive.
//  /_\        |
//   |    0..* | collections : dict<modelClassName, Collection>
//   |  +------v---------+
//   |  | <<Interface>>  |  A collection, as needed by ModelDeltaProcessor is
//   |  |   Collection   |  an object which allows inserting new items and
//   |  +----------------+  traverse existing items creating an Iterator.
//   |  | +insert(val)   |    +-----------------+
//   |  | +getIterator() |--->|  <<Interface>>  | 
//   |  +-------.--------+    |     Iterator    |  The iterator must allow
//   |         /_\            +-----------------+  retrieving, updating and
//   |          |             | +next() : obj   |  deleting items in the
//   |          |             | +hasNext()      |  collection.
//   |          |             | +update(newVal) |
//   |          |             | +delete()       |
//   |          |             +--------.--------+
//   |          |                     /_\
//   |          |                      |
//   |  +-----------------+   +-----------------+
//   |  | ArrayCollection |   |  ArrayIterator  |
//   |  +-----------------+   +-----------------+  ArrayCollection implements
//   |  | +array          |   | +next() : obj   |  these interfaces for regular 
//   |  +-----------------+   | +hasNext()      |  Javascript arrays.
//   |  | +insert(val)    |   | +update(newVal) |
//   |  | +getIterator()  |-->| +delete()       |
//   |  +-----------------+   +-----------------+
//   |                        
// +----------------------------+  (for AngularJS only)
// | ngCollectionDeltaProcessor |  ngCollectionDeltaProcessor wraps the call
// +----------------------------+  to onDelta() of the superclass in an
// | +scope                     |  AngularJS scope (using $apply).
// +----------------------------+                                            
// | +onDelta(delta)            |  This is needed for changes to be shown
// +----------------------------+  automatically on the screen.


var deltaProcessor = new ngCollectionDeltaProcessor();
deltaProcessor.onDelta = function(delta) {
   // Process delta on superclass
   ngCollectionDeltaProcessor.prototype.onDelta.call(this, delta);

   if (typeof(Notification) === "undefined")
      return;

   if (viewName == "allIssues") {
      // Alert on new issues
      for (var i = 0; i < delta.created.length; i++) {
         var item = delta.created[i];
         if (item.model_class_name == "Issue") {
            var issue = item.data;

            var title = "New issue from " + issue.initiator.first_name + " " +
               issue.initiator.last_name;
            var body = issue.title;

            new Notification(title, {body: body}).show();
         }
      }

      // Alert on existing issues that require attention
      for (var i = 0; i < delta.updated.length; i++) {
         var item = delta.updated[i];
         if (item.model_class_name == "Issue") {
            if (!item.old_data.needs_attention &&
                  item.new_data.needs_attention)
            {
               var title = "Issue requires attention";
               var body = item.new_data.title;

               new Notification(title, {body: body}).show();
            }
         }
      }
   } else if (viewName == "issue") {
      // Alert on replies, but not to the user that sends them
      for (var i = 0; i < delta.created.length; i++) {
         var item = delta.created[i];
         if (item.model_class_name == "IssueReply" &&
             item.data.author.email != userEmail) 
         {
            var title = deltaProcessor.scope.issue.title;
            var body = "A new reply has been received";

            new Notification(title, {body: body}).show();
         }
      }
   }
};

// Miau connector. Receives the URL, the protocol and the delta processor.
var miau = new MiauConnector(miauUrl, WebSocket, deltaProcessor);
miau.connect();

/* Controller (MVC) */

app.controller('AllIssuesCtrl', function($scope, Restangular) {
   // Sets the scope of the controller in the delta processor (needed by
   // ngCollectionDeltaProcessor).
   deltaProcessor.scope = $scope;

   $scope.formatAttention = function(attention) {
      return (attention ? "Needed" : "");
   };

   // This makes an AJAX call to GET /issues/ with an 'X-Miau' header set to
   // Subscribe.
   $scope.issues = [];
   Restangular.all('issues').getList({}, {'X-Miau': 'Subscribe'})
      .then(function(response) {
         // This function is called when the server replies

         // Assign the received data to issues model
         $scope.issues = response.data;

         // Tell the CollectionDeltaProcessor to process deltas over the
         // collection
         deltaProcessor.collections["Issue"] = new ArrayCollection($scope.issues);

         // Acquire the subscription with the token received
         var token = response.headers()['x-miau-token'];
         miau.acquireSubscription(token);
      });
});

app.controller('MyIssuesCtrl', function($scope, Restangular) {
   deltaProcessor.scope = $scope;

   $scope.issues = [];
   Restangular.all('my-issues').getList({}, {'X-Miau': 'Subscribe'})
      .then(function(response) {
         $scope.issues = response.data;
         deltaProcessor.collections["Issue"] = new ArrayCollection($scope.issues);
         var token = response.headers()['x-miau-token'];
         miau.acquireSubscription(token);
      });
});

app.controller('IssueCtrl', function($scope, Restangular) {
   deltaProcessor.scope = $scope;
   $scope.replies = [];
   Restangular.one('issues', issueId).get({}, {'X-Miau': 'Subscribe'})
      .then(function(response) {
         $scope.issue = response.data;
         $scope.replies = response.data.replies;

         // For single item updates
         deltaProcessor.collections["Issue"] = 
            new SingleItemCollection($scope.issue, function(newVal) {
               $scope.issue = newVal;
            });

         // For collection updates
         deltaProcessor.collections["IssueReply"] = 
               new ArrayCollection($scope.replies);

         var token = response.headers()['x-miau-token'];
         miau.acquireSubscription(token);
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
