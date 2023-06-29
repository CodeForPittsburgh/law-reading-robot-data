process.js: process.ts
	npx tsc process.ts

.PHONY: build
build: process.js
	docker compose build

.PHONY: run
run: build
	docker compose run convert "${URL}" "${FILE}"

.PHONY: clean
clean:
	rm -rf out
	rm process.js
