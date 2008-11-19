#!/usr/bin/python2.5

# This file is part of RSOD.
#
#    RSOD is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.


import web
from web import webapi
from web.contrib.template import render_mako
from subprocess import Popen, PIPE
import cPickle as pickle

# Mako for templating
render = render_mako(directories=['templates'], input_encoding='utf-8', output_encoding='utf8')

urls = (
    '/', 'index',
    '', 'index',
    '/create', 'create',
    '/request', 'request',
    '/manage/?([^/]*)/?(\d*)', 'manage'
)

# Welcome page
class index:
    def GET(self):
        title = "Start"
        return render.index(title=title);


# Creation of new tunnels
class create:
    db = None

    def __init__(self):
        self.db = webapi.ctx['environ']['db']

    def GET(self):
        title = "Create a tunnel"
        return render.create(title=title)

    def POST(self):
        args = web.input()
        tunnel = {
            "host": args["host"],
            "port": args["port"],
            "user": args["user"],
        }

        process = self.createTunnel(tunnel)
        tunnel['pid'] = process.pid

        if not self.db.data.has_key('tunnels'):
            self.db.data['tunnels'] = []

        self.db.data['tunnels'].append(tunnel)

        title = "Tunnel created"
        return render.tunnelCreated(title=title, tunnel=tunnel)
    
    def createTunnel(self, tunnel):
        return Popen("/usr/bin/ssh -nNT -R " + tunnel["port"] + ":localhost:22 " + tunnel["user"] + "@" + tunnel["host"], shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)


class request:
    def GET(self):
        title = "Create an RSOD Request"
        return render.request(title=title)

    def POST(self):
        title = "Create an RSOD Request"
        return render.request(title=title, request=True)
        

# Management of active tunnels
class manage:
    db = None

    def __init__(self):
        self.db = webapi.ctx['environ']['db']

    def GET(self, operation, id):
        if not operation or operation == 'list':
            return self.list()
        elif operation == 'close' and id:
            return self.close(id)

    def POST(self, operation, id):
        if operation == 'close' and id:
            return self.close(id)

    def list(self):
        title = "Manage active tunnels"
        if not self.db.data.has_key('tunnels'):
          self.db.data['tunnels'] = []

        tunnels = [tunnel for tunnel in self.db.data['tunnels'] if self.tunnel_exists(tunnel['pid'])]
        return render.list(title=title, tunnels=tunnels)

    def close(self, id):
        title = "Close tunnel(s)"
        
        if not self.tunnel_exists(id):
            message = "Tunnel with PID %s is not running." % id
            return render.close(title=title, message=message, closed=False)

        import os, signal, time
        signals = [signal.SIGTERM, signal.SIGKILL]
        for signal in signals:
            if self.tunnel_exists(id):
                try:
                    os.kill(int(id), signal)
                    os.wait()
                except OSError, (err, errstr):
                    print err
                    message = "Cannot close tunnel with PID %s. System said: %s" % (id, errstr)
                    return render.close(title=title, message=message, closed=False)
                time.sleep(1)

        if self.tunnel_exists(id):
            message = "Cannot close tunnel with PID %s" % id
            return render.close(title=title, message=message, closed=False)
       
        return render.close(title=title, closed=True)

    def close_confirm(self, id):
        title = "Close tunnel(s)"

        tunnel = None
        if self.tunnel_exists(id):
            tunnels = [tunnel for tunnel in self.db.data['tunnels'] if tunnel['pid'] == int(id)]
            tunnel = tunnels[0]
            # todo: if there are more than tunnel with the same PID only one must
            # be valid. 

        return render.close_confirm(title=title, tunnel=tunnel)

    def tunnel_exists(self, id):
        import os, errno, signal
        try:
            os.kill(int(id), 0)
            return True
        except OSError, err:
            return err.errno == errno.EPERM

# Basic abstraction of load/write for our cPickle-based database
class DB:
    data = None
    _db_path = "db/rsod.pkl"

    def __init__(self):
        self.load()

    def write(self):
        db = open(self._db_path, 'wb')
        pickle.dump(self.data, db)
        db.close()

    def load(self):
        import os

        if os.path.exists(self._db_path):
            db = open(self._db_path, 'rb')
            self.data = pickle.load(db)
            db.close()
        else:
            self.data = {}


# A WSGI Middleware which takes care of load and writing our database in the
# beginning and end of every request
class DBMiddleware:
    app = None
    db = None

    def __init__(self, app):
        self.app = app

    def __call__(self, environment, start_response):
        self.db = DB()
        environment['db'] = self.db
        response = self.app(environment, start_response)
        self.db.write()
        return response

if __name__ == "__main__":
    app = web.application(urls, globals(), autoreload=True)
    app.run(DBMiddleware)
