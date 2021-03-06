DOCKER_IMAGE?=mentor-classifier
ROOT=$(shell dirname ${PWD})
VENV=.venv
$(VENV):
	$(MAKE) $(VENV)-update

.PHONY: $(VENV)-update
$(VENV)-update:
	[ -d $(VENV) ] || python3.8 -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip
	$(VENV)/bin/pip install -r ./requirements.test.txt

.PHONY clean:
clean:
	rm -rf .venv htmlcov .coverage

.PHONY docker-build:
docker-build:
	docker build -t $(DOCKER_IMAGE) .

.PHONY docker-run-shell:
docker-run-shell:
	docker run -it --rm  --entrypoint /bin/bash $(DOCKER_IMAGE)

# use to test dockerized training locally
.PHONY: docker-train
docker-train-%:
	docker run \
		-it \
		--rm \
		-v $(PWD)/tests/fixtures/data/$*:/data \
		-v $(PWD)/tests/fixtures/shared:/shared \
		-v $(PWD)/tests/fixtures/models/$*:/output \
	$(DOCKER_IMAGE) train --data /data/ --shared /shared --output /output 

.PHONY: docker-train-default
docker-train-default:
	docker run \
		-it \
		--rm \
		-v $(PWD)/tests/fixtures/data/:/data \
		-v $(PWD)/tests/fixtures/shared:/shared \
		-v $(PWD)/tests/fixtures/models/default:/output \
	$(DOCKER_IMAGE) traindefault --data /data/ --shared /shared --output /output 

.PHONY: format
format: $(VENV)
	cd $(ROOT) && $(MAKE) format

.PHONY: license
license:
	cd $(ROOT) && make license

PHONY: test
test: $(VENV)
	rm -rf tests/fixtures/data_out/*/*
	cd $(ROOT)/shared && $(MAKE) installed/word2vec.bin
	cd $(ROOT)/shared && $(MAKE) installed/sentence-transformer
	cd $(ROOT)/shared && $(MAKE) installed/spacy-model
	. $(VENV)/bin/activate \
		&& coverage run \
			--omit="$(PWD)/tests $(VENV)" \
			-m py.test -vv $(args)

.PHONY: test-all
test-all: test-format test-lint test-types test-license test

.PHONY: test-format
test-format: $(VENV)
	cd $(ROOT) && $(MAKE) test-format

.PHONY: test-license
test-license: $(LICENSE) $(LICENSE_HEADER) $(VENV)
	cd $(ROOT) && $(MAKE) test-license

.PHONY: test-lint
test-lint: $(VENV)
	cd $(ROOT) && $(MAKE) test-lint

.PHONY: test-types
test-types: $(VENV)
	cd $(ROOT) && $(MAKE) test-types

.PHONY: update-deps
update-deps: $(VENV)
	. $(VENV)/bin/activate && pip-upgrade requirements*
