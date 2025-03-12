const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000';
const API_KEY = '3f8a9d5e-2c7b-4e6d-a9c5-d6b8e4c7f1a2';

class APIService {
    static async enhancePrompt(promptData) {
        try {
            const response = await fetch(`${API_BASE_URL}/enhance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': API_KEY
                },
                body: JSON.stringify(promptData)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
}

export default APIService;