// Display only the server's grounded AI plan. No skill-specific content is generated here.
export function learningPlan(report) {
  return (report?.gaps || []).map((gap) => ({
    ...gap,
    learn: gap.learn || [],
    resources: (gap.resources || []).filter((resource) => {
      try {
        const url = new URL(resource.url);
        return url.protocol === 'https:' && !url.username && !url.password;
      } catch {
        return false;
      }
    }),
  }));
}

export function hasLearningDetails(report) {
  const plans = learningPlan(report);
  return plans.length > 0 && plans.every((gap) =>
    gap.learn.some((step) => step.trim()) && gap.verify?.trim() && gap.resources.length > 0);
}
