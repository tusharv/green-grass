const samples = {
  ready: {
    key: 'ready',
    name: 'Ready to send',
    person: 'Avery Example',
    title: 'Frontend Developer',
    role: 'Frontend Developer',
    profile: {
      variant: 'ink',
      name: 'Avery Example',
      role_title: 'Frontend Developer',
      document: {
        contact: { name: 'Avery Example', email: 'avery@example.com', location: 'London, UK', links: ['https://example.com/avery'] },
        summary: 'Frontend developer with four years of experience building accessible web applications with React, JavaScript and TypeScript. Enjoys collaborating with product and design teams to turn complex workflows into clear interfaces.',
        skills: ['React', 'JavaScript', 'TypeScript', 'Accessibility', 'Design systems', 'Testing', 'CSS', 'HTML', 'Performance'],
        experience: [
          { employer: 'Northstar Studio', title: 'Frontend Developer', start: '2025', end: 'Present', bullets: ['Built a TypeScript dashboard with React for a logistics team, bringing daily shipment status into one accessible view.', 'Improved keyboard navigation and screen-reader labels across account and reporting flows.', 'Partnered with product designers to maintain a shared component library for account and reporting flows.'] },
          { employer: 'Paperplane Digital', title: 'Web Developer', start: '2023', end: '2025', bullets: ['Developed JavaScript features for customer portals and worked with designers to refine responsive layouts.', 'Wrote component tests for customer onboarding and account management journeys.'] },
          { employer: 'Common Thread', title: 'Junior Web Developer', start: '2022', end: '2023', bullets: ['Maintained CSS and HTML templates for a membership platform and resolved accessibility issues found in release reviews.'] },
        ],
        education: [{ school: 'Example Institute', credential: 'Diploma in Web Development', year: '2022' }, { school: 'Open Web Collective', credential: 'Accessible interfaces workshop', year: '2024' }],
      },
    },
    job: { company: 'Cedar Labs', title: 'Frontend Developer', description: 'Build accessible product interfaces using React, JavaScript and TypeScript. Three or more years of frontend experience preferred.', minYears: 3 },
    review: {
      suitable: true, yearsShown: 4, yearsNeeded: 3, coverage: 1, yearsScore: 1,
      required: [
        { name: 'React', present: true, source: 'work', quote: 'Built a TypeScript dashboard with React for a logistics team, bringing daily shipment status into one accessible view.' },
        { name: 'JavaScript', present: true, source: 'work', quote: 'Developed JavaScript features for customer portals and worked with designers to refine responsive layouts.' },
        { name: 'TypeScript', present: true, source: 'work', quote: 'Built a TypeScript dashboard with React for a logistics team, bringing daily shipment status into one accessible view.' },
      ],
      preferred: [{ name: 'Accessibility', present: true, source: 'work', quote: 'Improved keyboard navigation and screen-reader labels across account and reporting flows.' }],
    },
  },
  gaps: {
    key: 'gaps',
    name: 'Gaps to close',
    person: 'Morgan Example',
    title: 'Data Analyst',
    role: 'Data Analyst',
    profile: {
      variant: 'studio',
      name: 'Morgan Example',
      role_title: 'Data Analyst',
      document: {
        contact: { name: 'Morgan Example', email: 'morgan@example.com', location: 'Manchester, UK', links: ['https://example.com/morgan'] },
        summary: 'Early-career analyst who enjoys turning operational questions into clear, useful reports. Brings practical experience cleaning source data, documenting processes and helping teams act on weekly trends.',
        skills: ['Python', 'SQL', 'Excel', 'Data cleaning', 'Research', 'Written communication', 'Data documentation'],
        experience: [
          { employer: 'Fieldnote Co-op', title: 'Operations Assistant', start: '2025', end: 'Present', bullets: ['Used SQL to reconcile weekly order records and flag data quality issues for the operations team.', 'Prepared recurring Excel summaries for inventory and customer support colleagues.'] },
          { employer: 'Example Community Lab', title: 'Data Intern', start: '2024', end: '2025', bullets: ['Cleaned survey responses and documented a repeatable process for reviewing incoming records.', 'Prepared short written summaries of trends for a community research programme.'] },
          { employer: 'Signal Library', title: 'Research Volunteer', start: '2023', end: '2024', bullets: ['Checked survey entries for missing fields and organised feedback themes in a shared spreadsheet.'] },
        ],
        education: [{ school: 'Example College', credential: 'Certificate in Data Analytics', year: '2024' }, { school: 'Example College', credential: 'BA, Geography', year: '2023' }],
      },
    },
    job: { company: 'Harbor Metrics', title: 'Data Analyst', description: 'Analyze product usage with SQL, Python, Tableau and dbt. Role expects three years of experience. Excel is a plus.', minYears: 3 },
    review: {
      suitable: false, yearsShown: 2, yearsNeeded: 3, coverage: 0.5, yearsScore: 2 / 3,
      required: [
        { name: 'SQL', present: true, source: 'work', quote: 'Used SQL to reconcile weekly order records and flag data quality issues for the operations team.' },
        { name: 'Python', present: true, source: 'skills', quote: 'Python' },
        { name: 'Tableau', present: false, source: '', quote: '' },
        { name: 'dbt', present: false, source: '', quote: '' },
      ],
      preferred: [{ name: 'Excel', present: true, source: 'work', quote: 'Prepared recurring Excel summaries for inventory and customer support colleagues.' }],
    },
  },
};

export function getSample(key) {
  return samples[key] || null;
}

export function sampleScore(review) {
  return Math.round(100 * (0.7 * review.coverage + 0.3 * review.yearsScore));
}
