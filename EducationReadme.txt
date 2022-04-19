The images for this repository should already be built and running on your side. You probably don't need to
do anything in this repository unless an update is pushed.

However, if the front-end fails to start, then enter the following commands (it will take a long time):
1. python3 simoc.py teardown
2. python3 simoc.py setup
3. python3 simoc.py --with-dev-backend up