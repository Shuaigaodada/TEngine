clearCache:
	@echo "Clearing cache..."
	@rm -rf logs/*
	@echo "Cache cleared."

.PHONY: run

run:
	@files=$$(find . -name "$${f}.py"); \
    if [ -z "$$files" ]; then \
        echo "No Python file found"; \
    elif [ $$(echo "$$files" | wc -l) -gt 1 ]; then \
        echo "Multiple Python files found, please specify one:"; \
        echo "$$files"; \
    else \
        python3 $$files; \
    fi	

%:
	@: