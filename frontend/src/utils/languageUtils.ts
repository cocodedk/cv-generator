/**
 * Language utilities for consistent language handling across the application
 */

export const LANGUAGE_NAMES: { [key: string]: string } = {
  en: 'English',
  es: 'Spanish',
  fr: 'French',
  de: 'German',
  it: 'Italian',
  pt: 'Portuguese',
  nl: 'Dutch',
  ru: 'Russian',
  zh: 'Chinese',
  ja: 'Japanese',
  ko: 'Korean',
  ar: 'Arabic',
  da: 'Danish',
  sv: 'Swedish',
  no: 'Norwegian',
}

export const formatLanguage = (languageCode: string): string => {
  if (!languageCode) return 'Unknown'
  return LANGUAGE_NAMES[languageCode] || languageCode.toUpperCase()
}
