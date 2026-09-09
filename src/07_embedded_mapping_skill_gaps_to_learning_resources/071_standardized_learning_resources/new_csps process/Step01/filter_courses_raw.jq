.[] |
{
  id: .Identifier,

  title_en: (."Title/Titre (Eng)" // ""),
  description_en: (."Description (English/anglais)" // ""),
  link_en: (."Landing Page Link (En)" // ""),

  title_fr: (."Title/Titre (Fra)" // ""),
  description_fr: (."Description (French/français)" // ""),
  link_fr: (."Landing Page Link (Fr)" // ""),

  topics: (."Topics/Sujets" // ""),

  audience: (."Primary Intended Audience/Principal public cible" // ""),

  type: (."Delivery method/Mode de prestation" // ""),

  duration: (
    ."Duration - Product page" //
    ."Duration - Showcard" //
    ""
  ),

  domain: (
    ."Curriculum Architecture Placement/Emplacement dans l'architecture du curriculum"
    // ""
  ),

  subcategories: [
    (."If Transferable Skills, choose a subcategory/ Si Compétences transférables, choisir une sous-catégorie"),
    (."If Corporate Skills, choose a subcategory/ Si Compétences organisationnelles, choisir une sous-catégorie"),
    (."If Digital and Data, choose a subcategory/ Si Numérique et données , choisir une sous-catégorie"),
    (."If Healthy Workplace, choose a subcategory/ Si Milieu de travail sain, choisir une sous-catégorie"),
    (."If Public Sector Foundations, choose a subcategory/ Si Fondements du secteur public, choisir une sous-catégorie")
  ]
  | map(select(. != null and . != "")),

  related_courses: (."Related courses/Cours connexes" // "")
}