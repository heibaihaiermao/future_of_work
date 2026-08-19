
#rawDataCamp := "../../../../../generate-course-profiles/data/raw/all_courses.json"
rawDataCamp := "data/raw/dataCamp.json"
compProfile := data/competency_profile_cleaned.json

standardize: data/standard/csps.json

data/standard/csps.json: data/imputed/csps_with_competencies.json data/imputed/courses_with_competencies.json
	jq -s 'add' data/imputed/csps_with_competencies.json data/imputed/courses_with_competencies.json \
	| jq .[] -c > $@



data/standard/dataCamp.json: data/imputed/dataCamp.json
	jq --slurpfile raw ${rawDataCamp} -f filterDataCamp.jq $^ \
	| jq -c --slurpfile comps ${compProfile} \
	     -f join_competency_descriptions.jq > $@

# data/standard/csps.json: data/imputed/csps.json
# 	sed "s/foundational/Foundational/g; \
# 	     s/intermediate/Intermediate/g; \
# 	     s/advanced/Advanced/g; \
# 	     s/lead/Lead/g;" $^ \
# 	| jq -sf filterCSPS.jq \
# 	| jq -c --slurpfile comps ${compProfile} \
# 	     -f join_competency_descriptions.jq > $@

data/standard/onyxia.json: data/imputed/onyxia.json
	sed "s/foundational/Foundational/g; \
	     s/intermediate/Intermediate/g; \
	     s/advanced/Advanced/g; \
	     s/lead/Lead/g;" $^ \
	| jq -sf filterOnyxia.jq \
	| jq -c --slurpfile comps ${compProfile} \
	     -f join_competency_descriptions.jq > $@


PHONY: standardize

