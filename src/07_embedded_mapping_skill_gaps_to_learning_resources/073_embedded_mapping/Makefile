INPUT_DIR := data/0731_inputs
STAGING_DIR := data/0732_embeddings
OUTPUT_DIR := data/0733_recommendations

INPUT_FILES := $(wildcard $(INPUT_DIR)/gaps/*.json)
INPUT_RESOURCE_FILES := $(wildcard $(INPUT_DIR)/learning-resources/*.json)
STAGING_FILES := $(patsubst $(INPUT_DIR)/gaps/%.json,$(STAGING_DIR)/gaps/%_-_embedding_memory.json,$(INPUT_FILES))
STAGING_RESOURCE_FILES := $(patsubst $(INPUT_DIR)/learning-resources/%.json, $(STAGING_DIR)/learning-resources/%_-_embedding_memory.json, $(INPUT_RESOURCE_FILES))
OUTPUT_FILES := $(patsubst $(INPUT_DIR)/gaps/%.json,$(OUTPUT_DIR)/%_-_recommendations.json,$(INPUT_FILES))

recommendations: ${OUTPUT_FILES}
embedding: ${STAGING_FILES}
resource-embedding: ${STAGING_RESOURCE_FILES}


#${STAGING_DIR}/learning-resources_-_embedding_memory.json: ${INPUT_DIR}/learning-resources
#	python 0731_persistent_embedding.py $^

${STAGING_DIR}/gaps/%_-_embedding_memory.json: ${INPUT_DIR}/gaps/%.json 
	python persistent_embedding_0731.py $<

${STAGING_DIR}/learning-resources/%_-_embedding_memory.json: ${INPUT_DIR}/learning-resources/%.json 
	python persistent_embedding_0731.py $<

${OUTPUT_DIR}/%_-_recommendations.json: ${STAGING_DIR}/gaps/%_-_embedding_memory.json
	python embedded_recommends_0732.py $<


#output_file: input1.txt input2.txt
#	python script.py $<
#	python script.py input1.txt 
#
#	python script.py $^
#	python script.py input1.txt input2.txt

.PHONY: recommendations embedding resource-embedding
