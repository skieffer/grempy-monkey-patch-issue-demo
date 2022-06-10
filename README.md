This repo provides a minimal example, demonstrating an issue with
[gremlinpython](https://pypi.org/project/gremlinpython/3.6.0/),
which arises when attempting to connect to a gremlin server from within a view
function in a web app running on
[eventlet](https://pypi.org/project/eventlet/0.33.1/),
after eventlet monkey patching has been performed.

It also demonstrates a proposed solution, where we replace the
`AiohttpTransport` class with another `AbstractBaseTransport`
that is based on the `websocket-client` package, and does not
rely on `asyncio`.


## The problem

When several graph queries are fired off in rapid succession, the first few
result in the
```
RuntimeError: Cannot run the event loop while another loop is running
```
error being raised by `gremlinpython`'s use of `asyncio`, in its
`AiohttpTransport` class.

If we try to overcome the problem by setting
`call_from_event_loop=True` in our `DriverRemoteConnection`,
then we just get the opposite issue, with the
```
RuntimeError: There is no current event loop in thread 'GreenThread-2'.
```
error being raised instead.

Even attempts to set `call_from_event_loop` conditionally, based on a
test to see if we are in an `asyncio` event loop or not, lead to strange,
transient occurrences of `RuntimeError` saying there is no event loop.

The problem has been observed while using:
* Python 3.8, both natively on macOS, and in a Docker container hosted on macOS.
* gremlinpython versions: 3.6.0 and 3.5.2
* eventlet versions: 0.33.1 and 0.30.2


## Setup

After cloning the repository, go to its main dir, set up a virtual environment,
and install requirements:

```
python -m venv venv
. venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

## Demo

First start up the gremlin-server Docker container.
(It will be slow the first time if you don't have the image yet.)

```
./start_gremlin_server.sh
```

In a new terminal, start up the Flask app, with eventlet monkey patching:

```
. venv/bin/activate
python app.py mp
```

Now open a web browser, open the console in the developer tools,
and navigate to `localhost:5005`.
You should see several `500 (INTERNAL SERVER ERROR)` messages in the console.

Meanwhile, in the terminal where you started the web app, you should see
stack traces leading to the 
```
RuntimeError: Cannot run the event loop while another loop is running
```
error, several times.

The web app can be started in different configurations.
If you start it again without monkey patching:

```
python app.py
```

and redo the experiment, you should see no errors this time.

If you start the web app with both monkey patching and
the use of `call_from_event_loop=True` in the `DriverRemoteConnection`,

```
python app.py mp nest
```

and repeat the experiment, you will see a greater number of errors, this
time of the
```
RuntimeError: There is no current event loop in thread 'GreenThread-2'.
```
kind.


## Proposed solution

Run the experiment one more time, this time starting the web app with:

```
python app.py mp wst
```

This time we do eventlet monkey patching, but we also use our
`WebsocketTransport` class instead of `AiohttpTransport`.
When you load the page in the browser, you should see no errors.

The `WebsocketTransport` class is defined in the file `wst.py`.
It uses the `websocket-client` python package.


## Clean up

Stop the gremlin server:

```
./stop_gremlin_server.sh
```
