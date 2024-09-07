ACTIVATE := . ./venv/bin/activate &&

objects = $(wildcard *.in)
outputs = $(objects:.in=.txt)

all: $(outputs)

venv:
	python3 -m venv venv
	$(ACTIVATE) pip install -U pip
	$(ACTIVATE) pip install pip-tools
	touch -c venv

%.txt: %.in venv
	$(ACTIVATE) pip-compile --resolver=backtracking -v --output-file $@ $<


clean:
	@rm -f *.txt
	@rm -rf ./venv

.PHONY: all clean