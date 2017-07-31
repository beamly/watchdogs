# Example Docker Usage

See the `Dockerfile` in this directory for an example of how to run your own watchdogs tests in a Docker container.

## Building your configured version of watchdogs 
E.g. from the root of this repository:
```
docker build -t watchdogs-myorg:latest example_docker_usage/
```

## Running the tests
```
docker run -it watchdogs-myorg:latest
```
Note that the tests will run as part of the container start and the container will immediately terminate afterwards.
If you require the container to be long-lived, override the `ENTRYPOINT` in either your `Dockerfile` or the `docker run` command.
