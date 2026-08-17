#.[] | ."affected work-description elements"[] | {element, "element update reasoning"} + .gaps[] | {"development area": .name, description, "historic work": .element, "change to work": ."element update reasoning", justification} 

#.[] |
#  ."affected work-description elements"[] |
#    {element,
#     "element update reasoning"}
#    +
#    .gaps[]
#    |
#  {
#    "development area": .name,
#    description,
#    "historic work": .element,
#    "change to work": ."element update reasoning",
#    justification
#  }


limit(30;
  .[] |
    ."affected work-description elements"[] |
      {element,
       "element update reasoning"}
      +
      .gaps[] |
    {
      "development area": .name,
      description,
      "historic work": .element,
      "change to work": ."element update reasoning",
      justification
    }
)