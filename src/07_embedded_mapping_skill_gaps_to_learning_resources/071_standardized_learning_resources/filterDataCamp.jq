INDEX($raw[0].data[]; .title) as $raw_dict | 
	{title,
	 description,
	 "duration": $raw_dict[.title].timeNeededInHours,
	 technology,
 	 #topic?
	 "competencies": .proficiency |
				[(.[]? | {"competency": .SA, "proficiency": .PL} ) //
				 	 {"competency": ., "proficieny": "unknown"}]
}
