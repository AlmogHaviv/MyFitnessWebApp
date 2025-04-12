const API_BASE_URL = 'http://localhost:8000';

const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

export const createUserProfile = async (userData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/users`, {
      method: 'POST',
      headers: defaultHeaders,
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating user profile:', error);
    throw error;
  }
};

export const getWorkoutRecommendations = async (userId: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/recommendations/${userId}`, {
      method: 'GET',
      headers: defaultHeaders,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting workout recommendations:', error);
    throw error;
  }
};

export const getSimilarUsers = async (userId: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/similar-users/${userId}`, {
      method: 'GET',
      headers: defaultHeaders,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting similar users:', error);
    throw error;
  }
}; 