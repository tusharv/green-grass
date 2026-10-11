/**
 * Extract 1-2 uppercase characters from an email address or full name.
 * e.g., 'alex.morgan@example.com' -> 'AM', 'user@domain.com' -> 'U'
 */
export function getInitials(identifier) {
  if (!identifier || typeof identifier !== 'string') return '·';
  const clean = identifier.trim();
  if (!clean) return '·';

  // If identifier is an email, use the part before '@'
  const namePart = clean.includes('@') ? clean.split('@')[0] : clean;

  // Split by dots, underscores, dashes, or whitespace
  const parts = namePart.split(/[._\-\s]+/).filter(Boolean);
  if (parts.length >= 2) {
    const first = parts[0][0] || '';
    const second = parts[1][0] || '';
    return (first + second).toUpperCase();
  }
  if (parts.length === 1 && parts[0].length >= 2 && !clean.includes('@')) {
    return parts[0].slice(0, 2).toUpperCase();
  }
  return (parts[0]?.[0] || '·').toUpperCase();
}
