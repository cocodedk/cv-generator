export const mockProfileData = {
  personal_info: {
    name: 'John Doe',
    email: 'john@example.com',
  },
  experience: [{ title: 'Developer', company: 'Tech Corp', start_date: '2020-01' }],
  education: [{ degree: 'BS CS', institution: 'University', year: '2018' }],
  skills: [{ name: 'Python' }],
}

export const mockProfileDataWithMultipleExperiences = {
  personal_info: {
    name: 'John Doe',
  },
  experience: [
    { title: 'Developer', company: 'Tech Corp', start_date: '2020-01' },
    { title: 'Senior Dev', company: 'Big Corp', start_date: '2023-01' },
  ],
  education: [{ degree: 'BS CS', institution: 'University', year: '2018' }],
  skills: [],
}

export const mockCvData = {
  cv_id: 'test-cv-id',
  personal_info: {
    name: 'Jane Doe',
    email: 'jane@example.com',
  },
  experience: [{ title: 'Developer', company: 'Tech Corp', start_date: '2020-01' }],
  education: [{ degree: 'BS CS', institution: 'University', year: '2018' }],
  skills: [{ name: 'Python' }],
  theme: 'modern',
}

export const mockCvDataMinimal = {
  cv_id: 'test-cv-id',
  personal_info: { name: 'Test' },
  experience: [],
  education: [],
  skills: [],
}

export const mockCvDataForUpdate = {
  cv_id: 'test-cv-id',
  personal_info: { name: 'Jane Doe' },
  experience: [],
  education: [],
  skills: [],
}

export const mockCvResponse = {
  cv_id: 'test-id',
  filename: 'cv_test.docx',
  status: 'success',
}

export const mockUpdateResponse = {
  cv_id: 'test-cv-id',
  status: 'success',
}
