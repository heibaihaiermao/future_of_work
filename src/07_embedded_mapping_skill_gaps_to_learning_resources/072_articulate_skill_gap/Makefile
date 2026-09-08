INPUT_DIR := data/0721_identified
STAGING_DIR := data/0722_standard
OUTPUT_DIR := data/0723_articulated
JQ_SCRIPT := list_gaps.jq

INPUT_FILES := $(wildcard $(INPUT_DIR)/*.json)
STAGING_FILES := $(patsubst $(INPUT_DIR)/%.json,$(STAGING_DIR)/%.json,$(INPUT_FILES))
OUTPUT_FILES := $(patsubst $(INPUT_DIR)/%.json,$(OUTPUT_DIR)/%.json,$(INPUT_FILES))


articulate: ${OUTPUT_FILES}

# Minimal Change: Phony target triggers the output files list
list_gap: ${OUTPUT_FILES}

# Minimal Change: Static rule mapping output files directly to input files
${OUTPUT_DIR}/%.json: ${INPUT_DIR}/%.json ${JQ_SCRIPT}
	jq -cf ${JQ_SCRIPT} $< > $@

${STAGING_FILES}: ${INPUT_FILES} merge_schema.py 
	python merge_schema.py 

${OUTPUT_DIR}/%.json: ${STAGING_DIR}/%.json ${JQ_SCRIPT}
	jq -cf ${JQ_SCRIPT} $< > $@

.PHONY: articulate list_gap
