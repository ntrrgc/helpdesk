#!/usr/bin/env python

import logging
from tornado.web import Application
from tornado.ioloop import IOLoop
from snorky.services.datasync import DataSyncService, DataSyncBackend
from snorky.services.datasync.dealers import BroadcastDealer, SimpleDealer
from snorky.request_handlers.websocket import SnorkyWebSocketHandler
from snorky.request_handlers.http import BackendHTTPHandler
from snorky import ServiceRegistry


#-----------------------------------------------------------------------------#
# Dealers (model classes and filters)                                         #
#-----------------------------------------------------------------------------#

class AllIssues(BroadcastDealer):
    name = "AllIssues"
    model = "Issue"


class IssuesByUser(SimpleDealer):
    name = "IssuesByUser"
    model = "Issue"

    def get_key_for_model(self, model):
        return model['initiator']['email']


class Issue(SimpleDealer):
    name = "Issue"
    model = "Issue"

    def get_key_for_model(self, model):
        return model['id']


class IssueReplies(SimpleDealer):
    name = "IssueReplies"
    model = "IssueReply"

    def get_key_for_model(self, model):
        return model['issue_id']


#-----------------------------------------------------------------------------#
# Server startup                                                              #
#-----------------------------------------------------------------------------#
def gen_password():
    import random
    safe_random = random.SystemRandom()
    return "".join([
        safe_random.choice("abcdefghijklmnopqrstuvwxyz1234567890")
        for i in range(32)
    ])

def read_api_key():
    import errno
    try:
        with open('snorky-key', 'r') as f:
            password = f.read().strip()
    except IOError as error:
        if error.errno == errno.ENOENT:
            password = gen_password()
            with open('snorky-key', 'w') as f:
                f.write(password)
        else:
            raise error
    return password

if __name__ == "__main__":
    # Create two services
    datasync = DataSyncService("datasync", [
        AllIssues, IssuesByUser, Issue, IssueReplies,
    ])
    datasync_backend = DataSyncBackend("datasync_backend", datasync)

    logging.basicConfig(level=logging.INFO)

    # Register the frontend and backend services in different handlers
    frontend = ServiceRegistry([datasync])
    backend = ServiceRegistry([datasync_backend])

    # Create a WebSocket frontend
    app_frontend = Application([
        SnorkyWebSocketHandler.get_route(frontend, "/websocket"),
    ])
    app_frontend.listen(5001, address='localhost')

    # Create a backend, set a secret key, port and address
    app_backend = Application([
        ("/backend", BackendHTTPHandler, {
            "service_registry": backend,
            "api_key": read_api_key(),
        })
    ])
    app_backend.listen(5002, address='localhost')

    # Start processing
    try:
        IOLoop.instance().start()
    except KeyboardInterrupt:
        pass
