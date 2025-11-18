.PHONY: clean clean-non-10-23 clean-all

# Prefer repo venv python if present, otherwise fall back to python3
VENV_PY := .venv/bin/python
PY := $(if $(wildcard $(VENV_PY)),$(VENV_PY),python3)

# Inputs and outputs for 10-23 complexity reports
SPEC_BUNDLED := imported/10-23/openapi-10-23-bundled.yaml
SPEC_COMBINED := imported/10-23/gms-iei-10-23-combined.fixed.yaml
REPORT_BUNDLED := complexity-10-23.json
REPORT_COMBINED := complexity-10-23-combined.json
ASSESSMENT_COMBINED := ASSESSMENT-10-23-combined.md
SPEC_FDSN := fdsn.yaml
REPORT_FDSN := complexity-fdsn.json
ASSESSMENT_FDSN := ASSESSMENT-fdsn.md

# Regenerate reports and assessment for 10-23
reports-10-23: $(REPORT_BUNDLED) $(REPORT_COMBINED) $(ASSESSMENT_COMBINED)

$(REPORT_BUNDLED): $(SPEC_BUNDLED) tools/openapi_complexity.py
	$(PY) tools/openapi_complexity.py $< --json-out $@

$(REPORT_COMBINED): $(SPEC_COMBINED) tools/openapi_complexity.py
	$(PY) tools/openapi_complexity.py $< --json-out $@

$(ASSESSMENT_COMBINED): $(SPEC_COMBINED) tools/openapi_complexity.py
	$(PY) tools/openapi_complexity.py $< --json-out $(REPORT_COMBINED) --assessment-out $@

# FDSN reports
.PHONY: reports-fdsn
reports-fdsn: $(REPORT_FDSN) $(ASSESSMENT_FDSN)

$(REPORT_FDSN): $(SPEC_FDSN) tools/openapi_complexity.py
	$(PY) tools/openapi_complexity.py $< --json-out $@

$(ASSESSMENT_FDSN): $(SPEC_FDSN) tools/openapi_complexity.py
	$(PY) tools/openapi_complexity.py $< --json-out $(REPORT_FDSN) --assessment-out $@

# Aggregate: all reports
.PHONY: reports-all
reports-all: reports-10-23 reports-fdsn

clean: clean-non-10-23

clean-non-10-23:
	# Delete all complexity reports except 10-23 variants
	find . -maxdepth 1 -type f -name 'complexity-*.json' \
		! -name 'complexity-10-23.json' \
		! -name 'complexity-10-23-combined.json' -delete

clean-all:
	# Delete all complexity reports
	rm -f complexity-*.json
