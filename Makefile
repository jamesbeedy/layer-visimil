.PHONY: test
test:
	@tox

build:
	@charm build -rl DEBUG

push:
	@charm push `echo $(JUJU_REPOSITORY)`/builds/visimil cs:~jamesbeedy/visimil
