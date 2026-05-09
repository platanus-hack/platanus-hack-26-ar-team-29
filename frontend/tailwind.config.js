/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        card: 'var(--color-card)',
        line: 'var(--color-line)',
        input: 'var(--color-input)',
        foreground: 'var(--color-foreground)',
        muted: 'var(--color-muted)',
        subdued: 'var(--color-subdued)',
        accent: 'var(--color-accent)',
        'accent-hover': 'var(--color-accent-hover)',
        'accent-secondary': 'var(--color-accent-secondary)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
      },
      boxShadow: {
        card: '0 0 24px rgba(56, 217, 198, 0.03)',
        'card-hover': '0 0 30px rgba(56, 217, 198, 0.06)',
        'glow-xs': '0 0 15px rgba(56, 217, 198, 0.08)',
        glow: '0 0 20px rgba(56, 217, 198, 0.14)',
        logo: '0 0 10px rgba(56, 217, 198, 0.2)',
        'panel-glow': '0 0 40px rgba(56, 217, 198, 0.08)',
        'panel-glow-sm': '0 0 24px rgba(56, 217, 198, 0.08)',
        send: '0 0 28px rgba(56, 217, 198, 0.45)',
        'send-hover': '0 0 36px rgba(56, 217, 198, 0.65)',
        'success-soft': '0 0 10px rgba(62, 233, 138, 0.05)',
      },
    },
  },
  plugins: [],
};
