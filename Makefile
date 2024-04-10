REPORTS_FOLDER=reports


.PHONY: all clean release dev security


### default dev
### use make
all: dev

release:
	
dev:

clean:
	rm -rf $(REPORTS_FOLDER)/*.report

security: | $(REPORTS_FOLDER)
	trufflehog filesystem . | tee $(REPORTS_FOLDER)/trufflehog-filesystem.report  || true
	trufflehog git file://. | tee $(REPORTS_FOLDER)/trufflehog-git.report  || true
	gitleaks detect . | tee $(REPORTS_FOLDER)/gitleaks.report || true
	snyk test | tee $(REPORTS_FOLDER)/snyk.report   || true
	bandit -r . | tee $(REPORTS_FOLDER)/bandit.report || true


# Ensure the reports folder exists
$(REPORTS_FOLDER):
	mkdir -p $(REPORTS_FOLDER)