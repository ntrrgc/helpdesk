#!/usr/bin/env python
import tornado.ioloop
from miau.server.managers.subscription import SubscriptionManager
from miau.server.managers.dealer import DealerManager
from miau.server.facade import Facade
#from miau.server.frontend.sockjs import SockJSFrontend
from miau.server.frontend.websocket import WebSocketFrontend
from miau.server.dealers import Dealer, BroadcastDealer, SimpleDealer
from miau.server.backend import Backend


#-----------------------------------------------------------------------------#
# Dealers (model classes and filters)                                         #
#-----------------------------------------------------------------------------#

class AllIssues(BroadcastDealer):
    name = "AllIssues"
    model_class_name = "Issue"


class IssuesByUser(SimpleDealer):
    name = "IssuesByUser"
    model_class_name = "Issue"

    def get_key_for_model(self, model):
        return model['initiator']['email']


class Issue(SimpleDealer):
    name = "Issue"
    model_class_name = "Issue"

    def get_key_for_model(self, model):
        return model['id']


class IssueReplies(SimpleDealer):
    name = "IssueReplies"
    model_class_name = "IssueReply"

    def get_key_for_model(self, model):
        return model['issue_id']


#-----------------------------------------------------------------------------#
# Server startup                                                              #
#-----------------------------------------------------------------------------#
if __name__ == "__main__":
    dm = DealerManager()
    # Register dealers
    dm.register_dealer(AllIssues())
    dm.register_dealer(IssuesByUser())
    dm.register_dealer(Issue())
    dm.register_dealer(IssueReplies())

    sm = SubscriptionManager()
    io_loop = tornado.ioloop.IOLoop.instance()
    facade = Facade(dm, sm, io_loop)

    # Create a backend, set a secret key, port and address
    backend = Backend(facade, secret_key="JkdXZCQgsCIpFAA7GsPY")
    backend.listen(5001, address='127.0.0.1')

    # You can use WebSocketFrontend or SockJSFrontend
    frontend = WebSocketFrontend(facade)
    frontend.listen(5002, address='0.0.0.0')

    # Start processing
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
