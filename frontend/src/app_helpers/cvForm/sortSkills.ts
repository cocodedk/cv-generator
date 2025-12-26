import { Skill } from '../../types/cv'

/**
 * Sort skills grouped by category, then by name and level within each category.
 * Skills without a category are grouped under an empty string category.
 *
 * @param skills - Array of skills to sort
 * @returns Sorted array of skills grouped by category
 */
export function sortSkillsByCategory(skills: Skill[] | undefined | null): Skill[] {
  if (!skills || !Array.isArray(skills) || skills.length === 0) {
    return []
  }

  // Group skills by category
  const skillsByCategory = new Map<string, Skill[]>()
  for (const skill of skills) {
    const category = skill.category || ''
    if (!skillsByCategory.has(category)) {
      skillsByCategory.set(category, [])
    }
    skillsByCategory.get(category)!.push(skill)
  }

  // Sort categories alphabetically (empty string goes last)
  const sortedCategories = Array.from(skillsByCategory.keys()).sort((a, b) => {
    if (a === '') return 1
    if (b === '') return -1
    return a.localeCompare(b)
  })

  // Sort skills within each category by name, then by level
  const sortedSkills: Skill[] = []
  for (const category of sortedCategories) {
    const categorySkills = skillsByCategory.get(category)!
    categorySkills.sort((a, b) => {
      // First sort by name
      const nameCompare = (a.name || '').localeCompare(b.name || '')
      if (nameCompare !== 0) {
        return nameCompare
      }
      // If names are equal, sort by level
      return (a.level || '').localeCompare(b.level || '')
    })
    sortedSkills.push(...categorySkills)
  }

  return sortedSkills
}
