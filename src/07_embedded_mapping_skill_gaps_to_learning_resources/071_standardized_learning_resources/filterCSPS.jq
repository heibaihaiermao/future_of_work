.[] |
	{
	 #"id": .Identifier,
	 "title": (."Title/Titre (Eng)" / " (")[0],
	 "description": ."Description (English/anglais)",
	 "duration": (."Duration - Showcard" / "/")[0],
	 "technology": "theory",
	 "competencies": .proficiency | [(.[]? | {"competency": .SA, "proficiency": .PL} ) //
				 	 {"competency": ., "proficiency": "unknown"}]
}
