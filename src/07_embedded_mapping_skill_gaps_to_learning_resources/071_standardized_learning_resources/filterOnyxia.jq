.[] |
	{"title": .name | (.en? // .fr? // .),
	 "description": .Description | (.en? // .fr? // .),
	 "duration": null,
	 "technology": .imputed_technology.technology,
	 "competencies": .proficiency | [
				(.[]? | {"competency": .SA, "proficiency": .PL}) // 
					{"competency": ., "proficiency": "unknown"}]}
