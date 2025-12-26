import {
  Address,
  CVData,
  Education,
  Experience,
  PersonalInfo,
  ProfileData,
  Project,
  Skill,
} from '../../types/cv'

function toOptionalString(value: string | undefined): string | undefined {
  const trimmed = value?.trim()
  return trimmed ? trimmed : undefined
}

function normalizeAddress(address: Address | undefined): Address | undefined {
  if (!address) return undefined

  const normalized: Address = {
    street: toOptionalString(address.street),
    city: toOptionalString(address.city),
    state: toOptionalString(address.state),
    zip: toOptionalString(address.zip),
    country: toOptionalString(address.country),
  }

  return Object.values(normalized).some(value => value) ? normalized : undefined
}

function normalizePersonalInfo(personalInfo: PersonalInfo): PersonalInfo {
  return {
    name: personalInfo.name.trim(),
    title: toOptionalString(personalInfo.title),
    email: toOptionalString(personalInfo.email),
    phone: toOptionalString(personalInfo.phone),
    address: normalizeAddress(personalInfo.address),
    linkedin: toOptionalString(personalInfo.linkedin),
    github: toOptionalString(personalInfo.github),
    website: toOptionalString(personalInfo.website),
    summary: toOptionalString(personalInfo.summary),
    photo: personalInfo.photo || undefined,
  }
}

function normalizeProjects(projects: Project[] | undefined): Project[] | undefined {
  if (!projects?.length) return undefined
  return projects.map(project => ({
    name: project.name.trim(),
    description: toOptionalString(project.description),
    highlights: project.highlights?.filter(Boolean),
    technologies: project.technologies?.filter(Boolean),
    url: toOptionalString(project.url),
  }))
}

function normalizeExperience(experience: Experience[]): Experience[] {
  return experience.map(item => ({
    title: item.title.trim(),
    company: item.company.trim(),
    start_date: item.start_date.trim(),
    end_date: toOptionalString(item.end_date),
    description: toOptionalString(item.description),
    location: toOptionalString(item.location),
    projects: normalizeProjects(item.projects),
  }))
}

function normalizeEducation(education: Education[]): Education[] {
  return education.map(item => ({
    degree: item.degree.trim(),
    institution: item.institution.trim(),
    year: toOptionalString(item.year),
    field: toOptionalString(item.field),
    gpa: toOptionalString(item.gpa),
  }))
}

function normalizeSkills(skills: Skill[]): Skill[] {
  return skills.map(item => ({
    name: item.name.trim(),
    category: toOptionalString(item.category),
    level: toOptionalString(item.level),
  }))
}

export function normalizeCvDataForApi(data: CVData): CVData {
  return {
    personal_info: normalizePersonalInfo(data.personal_info),
    experience: normalizeExperience(data.experience),
    education: normalizeEducation(data.education),
    skills: normalizeSkills(data.skills),
    theme: data.theme,
  }
}

export function normalizeProfileDataForApi(data: ProfileData): ProfileData {
  return {
    personal_info: normalizePersonalInfo(data.personal_info),
    experience: normalizeExperience(data.experience),
    education: normalizeEducation(data.education),
    skills: normalizeSkills(data.skills),
  }
}
