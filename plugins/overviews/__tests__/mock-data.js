export function getMockTimelineGraph() {
  return [
    {
      name: 'S&P Global Ratings Sovereign Rating Methodology (2017)',
      type: 'Summary',
      timestamp: '2026-07-05T16:25:57Z',
      tags: ['Credit Ratings', 'Sovereigns'],
      filePath: 'summaries/SP.md',
      properties: {
        title: 'S&P Global Ratings Sovereign Rating Methodology (2017)',
        tags: ['Credit Ratings', 'Sovereigns'],
        times: [
          {
            date: '2011-02-16',
            title: 'Publication of Principles of Credit Ratings'
          }
        ]
      }
    },
    {
      name: 'Principles of Credit Ratings',
      type: 'Concept',
      timestamp: '2026-07-05T16:25:57Z',
      tags: [],
      filePath: 'collections/concept/principles.md',
      properties: {
        title: 'Principles of Credit Ratings'
      }
    }
  ];
}

export function getMockSocialGraph() {
  return [
    {
      name: 'Sovereign Summary',
      type: 'Summary',
      timestamp: '2026-07-05T16:25:57Z',
      tags: [],
      filePath: 'summaries/SP.md',
      properties: {
        title: 'Sovereign Summary'
      }
    },
    {
      name: 'Alex Stomper',
      type: 'Person',
      timestamp: '2026-07-05T16:25:57Z',
      tags: [],
      filePath: 'collections/persons/Alex Stomper.md',
      properties: {
        title: 'Alex Stomper',
        relationships: [
          {
            person: 'Financial Economics',
            relation: 'lectured on'
          }
        ]
      }
    },
    {
      name: 'Christine Lagarde',
      type: 'Person',
      timestamp: '2026-07-05T16:25:57Z',
      tags: [],
      filePath: 'collections/persons/Christine Lagarde.md',
      properties: {
        title: 'Christine Lagarde',
        relationships: [
          {
            person: 'Clyde Caruana',
            relation: 'consulted with'
          }
        ]
      }
    }
  ];
}
