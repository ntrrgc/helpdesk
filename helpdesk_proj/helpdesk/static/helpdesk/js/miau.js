'use strict';

var MiauConnector = function(address, socketClass, deltaProcessor, debug) {
   this.address = address;
   this.socketClass = socketClass;
   this.deltaProcessor = deltaProcessor;
   this.debug = (typeof(debug) != "undefined" ? debug : false);
}

MiauConnector.prototype._nextCallId = 0;
MiauConnector.prototype._callbacks = {};
MiauConnector.prototype._socket = null;
MiauConnector.prototype._callOnOpen = [];
MiauConnector.prototype.connected = false;
MiauConnector.prototype.connecting = false;
MiauConnector.prototype.debug = false;

MiauConnector.prototype.connect = function(done) {
   var self = this;

   this._socket = new this.socketClass(this.address);
   this._socket.onopen = function() {
      if (self.debug && typeof console == "object") {
         console.log("Connected to Miau server.");
      }
      self.connected = true;
      self.connecting = false;
      if (done) {
         done.apply(self, arguments);
      }

      /* _callOnOpen is populated by acquireSubscription when the socket
       * is not connected yet */
      for (var i in self._callOnOpen) {
         self._callOnOpen[i].call(self);
      }
      self._callOnOpen = [];
   }
   this._socket.onmessage = function() {
      self._onMessage.apply(self, arguments);
   };
   this._socket.onclose = function () {
      self._onClose.apply(self, arguments);
   };
   
   this.connecting = true;
};

MiauConnector.prototype.disconnect = function() {
   this._socket.close();
   this._socket = null;
}

MiauConnector.prototype.callFunction = function(name, args, done) {
   var callId = this._nextCallId++;
   var message = {
      'call_id': callId,
      'function': name,
   };
   
   for (var key in args) {
      message[key] = args[key];
   }

   // Set callback for response
   if (done) {
      this._callback[callId] = done;
   }

   if (this.debug && typeof console == "object") {
      console.log("Miau: ", name, args);
   }

   this._socket.send(JSON.stringify(message));
};

MiauConnector.prototype._onMessage = function(ev) {
   var msg;
   try {
      msg = JSON.parse(ev.data);
   } catch (SyntaxError) {
      if (typeof console == "object") {
         console.error("Miau: Received a malformed message (syntax error): ",
               ev.data);
      }
      return;
   }

   if (msg.type == "function_response") {
      if (this.debug && typeof console == "object") {
         console.log("Miau: Function response", msg);
      }

      // Call callback, if any
      var call_id = msg.call_id;
      if (call_id in this._callbacks) {
         this._callbacks[call_id](msg);
         delete this._callbacks[call_id];
      }
   } else if (msg.type == "delta") {
      if (this.debug && typeof console == "object") {
         console.log("Miau: Delta ", msg);
      }

      // Deliver to the application
      this.deltaProcessor.onDelta(msg);
   } else {
      // Show error (even if not in debug mode)
      if (typeof console == "object") {
         console.error("Miau: Received unsupported message: ");
         console.error(ev.data);
      }
   }
};

MiauConnector.prototype._onClose = function(ev) {
   if (this.debug && typeof console == "object") {
      console.log("Miau: Connection lost.");
   }
   this.connecting = false;
   this.connected = false;
};

MiauConnector.prototype.acquireSubscription = function f(token, done) {
   if (this.connected) {
      // If connected, just send message
      var args = {'token': token};
      return this.callFunction('acquire_subscription', args, done);
   } else {
      // If not connected yet, call this again when the socket is connected
      var args = arguments;
      this._callOnOpen.push(function() { f.apply(this, args); });
   }
};

MiauConnector.prototype.cancelSubscription = function(token, done) {
   var args = {'token': token};
   return this.callFunction('cancel_subscription', args, done);
};

var CollectionDeltaProcessor = function() {
};

CollectionDeltaProcessor.prototype.collections = {};

CollectionDeltaProcessor.prototype.onDelta = function(delta) {
   for (var i in delta.created) {
      var deltaItem = delta.created[i];
      var container = this.collections[deltaItem.model_class_name];
      container.insert(deltaItem.data);
   }

   for (var i in delta.updated) {
      var deltaItem = delta.updated[i];
      var container = this.collections[deltaItem.model_class_name];
      
      var needle = deltaItem.old_data;
      var iterator = container.getIterator();
      while (iterator.hasNext()) {
         var item = iterator.next();
         if (item.id == needle.id) {
            iterator.update(deltaItem.new_data);
            break;
         }
      }
   }

   for (var i in delta.deleted) {
      var deltaItem = delta.deleted[i];
      var container = this.collections[deltaItem.model_class_name];
      
      var needle = deltaItem.data;
      var iterator = container.getIterator();
      while (iterator.hasNext()) {
         var item = iterator.next();
         if (item.id == needle.id) {
            iterator.remove();
         }
      }
   }
};

/* ngCollectionDeltaProcessor does the same as CollectionDeltaProcessor,
 * wrapped in a scope. (for AngularJS only) */

var ngCollectionDeltaProcessor = function(scope) {
   this.scope = scope;
}

ngCollectionDeltaProcessor.prototype = new CollectionDeltaProcessor();
ngCollectionDeltaProcessor.prototype.constructor = ngCollectionDeltaProcessor;

ngCollectionDeltaProcessor.prototype.onDelta = function(delta) {
   var self = this;
   this.scope.$apply(function () {
      CollectionDeltaProcessor.prototype.onDelta.call(self, delta);
   });
}

/* Data container and iterator for array */

var ArrayIterator = function(array) {
   this.array = array;
}

ArrayIterator.prototype.array = null;
ArrayIterator.prototype.index = -1;

ArrayIterator.prototype.hasNext = function() {
   var lastIndex = this.array.length - 1;
   return (this.index < lastIndex);
}

ArrayIterator.prototype.next = function() {
   if (!this.hasNext()) {
      throw("Busted iterator")
   }
   return this.array[++this.index];
}

ArrayIterator.prototype.remove = function() {
   if (this.lastIndex == -1) {
      throw("Iterator not pointing to an item! (call next())");
   }
   this.array.splice(this.index--, 1);
}

ArrayIterator.prototype.update = function(newVal) {
   if (this.lastIndex == -1) {
      throw("Iterator not pointing to an item! (call next())");
   }
   this.array[this.index] = newVal;
}


var ArrayCollection = function(array) {
   this.array = array;
}

ArrayCollection.prototype.array = null;

ArrayCollection.prototype.insert = function(val) {
   this.array.push(val);
}

ArrayCollection.prototype.getIterator = function() {
   return new ArrayIterator(this.array);
}

/* Virtual single-item collection and iterator */

var SingleItemIterator = function(collection) {
   this.fetched = false;
   this.collection = collection;
}

SingleItemIterator.prototype.fetched = false;
SingleItemIterator.prototype.collection = null;

SingleItemIterator.prototype.hasNext = function() {
   return !this.fetched;
}

SingleItemIterator.prototype.next = function() {
   if (this.fetched) {
      throw("Busted iterator");
   }
   this.fetched = true;
   return this.collection.item;
}

SingleItemIterator.prototype.remove = function() {
   if (!this.fetched) {
      throw("Iterator not pointing to an item! (call next())");
   }
   this.collection.removeHandler();
}

SingleItemIterator.prototype.update = function(newVal) {
   if (!this.fetched) {
      throw("Iterator not pointing to an item! (call next())");
   }
   this.collection.updateHandler(newVal);
}


var SingleItemCollection = function(item, updateHandler, removeHandler) {
   this.item = item;
   this.updateHandler = updateHandler;
   this.removeHandler = removeHandler || function () {};
}

SingleItemCollection.prototype.item = null;

SingleItemCollection.prototype.insert = function(val) {
   // No action
}

SingleItemCollection.prototype.getIterator = function() {
   return new SingleItemIterator(this);
}
