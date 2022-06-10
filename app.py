import sys
switches = set(sys.argv[1:])

# The following switches can be passed on the command line:
#
# mp:   do eventlet monkey patching
# nest: set call_from_event_loop=True
# wst:  use our WebsocketTransport instead of AiohttpTransport

if 'mp' in switches:
    print('Monkey patching...')
    import eventlet
    eventlet.monkey_patch()

    """
    # Note: tried using eventlet's `import_patched()`
    # (see http://eventlet.net/doc/patching.html#import-green)
    # like this:

    anon_trav = eventlet.import_patched('gremlin_python.process.anonymous_traversal')
    traversal = anon_trav.traversal
    drc = eventlet.import_patched('gremlin_python.driver.driver_remote_connection')
    DriverRemoteConnection = drc.DriverRemoteConnection

    # instead of the ordinary imports that appear below, but this did not
    # solve the issue either. Instead, we got this error at startup:

    Traceback (most recent call last):
      File "app.py", line 35, in <module>
        remote = DriverRemoteConnection(GRAPHDB_URI, call_from_event_loop=NEST)
      File "/Users/skieffer/workspace/gremlinpython_issue_demo/venv/lib/python3.8/site-packages/gremlin_python/driver/driver_remote_connection.py", line 68, in __init__
        self._client = client.Client(url, traversal_source,
      File "/Users/skieffer/workspace/gremlinpython_issue_demo/venv/lib/python3.8/site-packages/gremlin_python/driver/client.py", line 93, in __init__
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
      File "/Users/skieffer/.pyenv/versions/3.8.12/lib/python3.8/concurrent/futures/thread.py", line 147, in __init__
        self._work_queue = queue.SimpleQueue()
      AttributeError: module 'eventlet.green.Queue' has no attribute 'SimpleQueue'
    """

NEST=None
if 'nest' in switches:
    print('Will set call_from_event_loop=True')
    NEST=True

from flask import Flask
from flask_socketio import SocketIO

from gremlin_python.process.anonymous_traversal import traversal
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection

import wst

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=True, engineio_logger=True)

tfact = None
if 'wst' in switches:
    print('Will use the WebsocketTransport')
    tfact = wst.transport_factory 

GRAPHDB_URI='ws://localhost:8182/gremlin'
remote = DriverRemoteConnection(
    GRAPHDB_URI,
    transport_factory=tfact,
    call_from_event_loop=NEST
)
gt = traversal().withRemote(remote)

page = """
<html>
<head>
<style>
body {
    background: #222;
    color: #eee;
}
</style>
</head>
<body>
See console
<script>
for (let i = 0; i < 10; i++) {
    fetch('/query1').then(console.log);
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return page

@app.route("/query1")
def query1():
    results = gt.V().has('foo', 'bar').elementMap().toList()
    return str(results)

if __name__ == '__main__':
    socketio.run(app, port=5005)

