INPUT_DIR := data/0731_inputs
STAGING_DIR := data/0732_embeddings
OUTPUT_DIR := data/0733_recommendations

INPUT_FILES := $(wildcard $(INPUT_DIR)/gaps/*.json)
STAGING_FILES := $(patsubst $(INPUT_DIR)/gaps/%.json,$(STAGING_DIR)/gaps/%_-_embedding_memory.json,$(INPUT_FILES))
OUTPUT_FILES := $(patsubst $(INPUT_DIR)/gaps/%_-_proposed_updates.json,$(OUTPUT_DIR)/%_-_recommendations.json,$(INPUT_FILES))

recommendations: ${OUTPUT_FILES}
embedding: ${STAGING_FILES}


#${STAGING_DIR}/learning-resources_-_embedding_memory.json: ${INPUT_DIR}/learning-resources
#	python 0731_persistent_embedding.py $^

${STAGING_DIR}/gaps/%_-_embedding_memory.json: ${INPUT_DIR}/gaps/%.json 
	python persistent_embedding_0731.py $<

${OUTPUT_DIR}/%_-_recommendations.json: ${STAGING_DIR}/gaps/%_-_proposed_updates_-_embedding_memory.json
	python embedded_recommends_0732.py $<

.PHONY: recommendations embedding
