.[] |
{
  id: .Identifier,

  title_en: (."Title/Titre (Eng)" // ""),
  description_en: (."Description (English/anglais)" // ""),
  link_en: (."Catalogue Link (EN)" // ""),

  title_fr: (."Title/Titre (Fra)" // ""),
  description_fr: (."Description (French/français)" // ""),
  link_fr: (."Catalogue Link (FR)" // ""),

  topics: (."Topics/Sujets" // ""),

  audience: (."Primary Intended Audience/Public ciblé principal" // ""),

  type: (."Type of product/ Type de produit" // ""),

  # Prefer explicit product page duration, fallback to showcard
  duration: (
    ."Duration - Product page" //
    ."Duration - Showcard" //
    ""
  ),

  domain: (
    ."Curriculum Architecture Placement/Emplacement dans l'architecture du curriculum" // ""
  ),

  subcategories: [
    (."If Corporate Skills, choose a sub-category/ Si Compétences organisationnelles, choisir une sous-catégorie"),
    (."If Digital and Data, choose a sub-category/ Si numérique et données , choisir une sous-catégorie"),
    (."If Healthy Workplace, choose a sub-category/ Si milieu de travail sain, choisir une sous-catégorie"),
    (."If Public Sector Foundations, choose a sub-category/ Si fondements du secteur public, choisir une sous-catégorie"),
    (."If Transferable Skills, choose a sub-category/ Si compétences transférables, choisir une sous-catégorie")
  ]
  | map(select(. != null and . != "")),

  related_courses: (."Related courses/Cours connexes" // "")
}