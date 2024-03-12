clearCache:
	@echo "Clearing cache..."
	@rm -rf logs/*
	@echo "Cache cleared."

.PHONY: run

test:
	@python tests/afa/$(file).py