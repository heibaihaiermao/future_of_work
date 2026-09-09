INDEX(($comps[0] | .behavioural_competencies[],
		   .technical_competencies[],
		   .technical_knowledge[]); .name) as $comps_dict |
	. + {"competencies": ([.competencies[] | .
					  + ({"description": $comps_dict[.competency].description})
					  + ({"indicators": ($comps_dict[.competency].proficiency_levels[.proficiency])})])}
