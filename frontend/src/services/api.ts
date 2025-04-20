const API_BASE_URL = 'http://localhost:8000';

const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

export const createUserProfile = async (userData: any) => {
  try {
    // Remove the gender conversion and send the data as is
    console.log('API call data:', userData);
    
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),  // Send the original userData without modification
    });

    if (!response.ok) {
      const errorData = await response.json();
      console.error('API error:', errorData);
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call error:', error);
    throw error;
  }
};


export const getSimilarUsers = async (userData: any) => {
  try {
    const response = await fetch(`${API_BASE_URL}/similar-users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting similar users:', error);
    throw error;
  }
};

export const logEvent = async (userId: string, buddyId: string, action: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/log-event`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: userId,
        buddy_id: buddyId,
        action: action,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error logging event:', error);
    throw error;
  }
};

export const createWorkout = async (workoutData: { id_number: number; workout_type: string }) => {
  try {
    const response = await fetch(`${API_BASE_URL}/workouts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(workoutData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `Failed to create workout: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error creating workout:', error);
    throw error;
  }
};

export const getUserById = async (userId: number) => {
  try {
    const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
      method: 'GET',
      headers: defaultHeaders,
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `User fetch failed: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching user by ID:', error);
    throw error;
  }
};
