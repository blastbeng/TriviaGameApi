#!/bin/sh
docker build . -f ./Dockerfile.trivia_api  -t trivia-game-api:latest
