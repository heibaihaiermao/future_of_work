CSPS_CSV := OPL with Catalogue Links (Active other products).csv
COURSES_CSV := Course OPL with Catalogue Links (Active courses).csv

all: csps_clean.json courses_clean.json

csps_raw.json:
	python -c "import csv, json; f=open('$(CSPS_CSV)', encoding='utf-8'); data=list(csv.DictReader(f)); json.dump(data, open('csps_raw.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)"

csps_clean.json: csps_raw.json
	jq -f filterCSPS_raw.jq csps_raw.json > csps_clean.json

courses_raw.json:
	python -c "import csv, json; f=open('$(COURSES_CSV)', encoding='utf-8-sig'); data=list(csv.DictReader(f)); json.dump(data, open('courses_raw.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)"

courses_clean.json: courses_raw.json
	jq -f filter_courses_raw.jq courses_raw.json > courses_clean.json

clean:
	del csps_raw.json courses_raw.json

.PHONY: all clean