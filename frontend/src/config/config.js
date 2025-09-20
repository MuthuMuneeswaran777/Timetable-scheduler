// Configuration file for different environments
const config = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
    APP_NAME: 'Timetable Management System',
    VERSION: '1.0.0'
  },
  production: {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://your-api-domain.com',
    APP_NAME: 'Timetable Management System',
    VERSION: '1.0.0'
  }
};

// Determine current environment
const environment = import.meta.env.MODE || 'development';

// Export the appropriate config
export default config[environment] || config.development;

// Helper function to get API URL
export const getApiUrl = (endpoint = '') => {
  const baseUrl = config[environment]?.API_BASE_URL || config.development.API_BASE_URL;
  return `${baseUrl}${endpoint}`;
};
